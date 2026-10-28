"""Build a published Lua editor update without replacing the V3 recovery core."""
import argparse
import difflib
import hashlib
import json
import secrets
import zipfile
import zlib
from pathlib import Path
from build import load_backup
from source import current_source

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def literal(data):
    for n in range(1,20):
        eq=b'='*n
        if b']'+eq+b']' not in data:
            # Prefix with a sentinel so Lua's long-string newline handling never
            # strips an inserted first newline from a patch.
            return b'(['+eq+b'[!'+data+b']'+eq+b']):sub(2)'
    raise ValueError('Cannot delimit source')

def isolated_source(source,slot):
    """Bind an ordinary candidate source to the slot its loader will validate."""
    if isinstance(slot,bool) or not isinstance(slot,int) or slot not in range(4,121):
        raise ValueError('Choose a user slot 4-120')
    # Lua long strings normalize CRLF; checksum the same bytes they reconstruct.
    return f'local SIDE_SLOT={slot}\n'.encode()+source.replace(b'\r\n',b'\n')


def payload(base,updated,slot,build_id):
    nodes=[]
    oldlines=base.splitlines(keepends=True);newlines=updated.splitlines(keepends=True)
    offsets=[0]
    for line in oldlines:offsets.append(offsets[-1]+len(line))
    for tag,a,b,c,d in difflib.SequenceMatcher(None,oldlines,newlines,autojunk=False).get_opcodes():
        if tag=='equal':nodes.append(('{%d,%d}'%(offsets[a]+1,offsets[b])).encode())
        elif tag in ('replace','insert'):nodes.append(b'('+literal(b''.join(newlines[c:d]))+b')')
    patch=b'{'+b',\n'.join(nodes)+b'}'
    start=b'''-- Side editor update: normal Lua program; keep V3 entries 1, 2, 3.
local parent=assert(seedsow_editor,'Load through a V3 user slot')
local initial=parent.test_state()
assert(initial.slot==SIDE_SLOT,'Publish this side editor to user slot SIDE_SLOT before running it')
local previous_guard=initial.guard
initial.guard=false -- bounded reconstruction runs once on the next frame
local once=false
return function(engine)
 if once then return end
 once=true
 local prior=parent.test_state()
 prior.guard=previous_guard
 local W=parent.storage
 local basepath=engine:var('s.savepath')
 local base
 for i=1,3 do
  local data=W.read(basepath,'ssedit'..i..'.lua')
  if data and W.adler(data)==BASE_CRC then base=data break end
 end
 assert(base,'This update needs the retained V3 base; no recovery file was changed')
 local patch=PATCH_DATA
 local parts={}
 for i,p in ipairs(patch) do parts[i]=type(p)=='table' and base:sub(p[1],p[2]) or p end
 local source=table.concat(parts)
 assert(#source==SOURCE_SIZE and W.adler(source)==SOURCE_CRC,'Update reconstruction failed; recovery unchanged')
 local chunk=assert(loadstring(source,'@side-editor-BUILD_ID'))
 local names={'seedsow_editor_frame','seedsow_editor_key','seedsow_editor_event','seedsow_editor_keyboard_returned'}
 local callbacks={}
 for _,name in ipairs(names) do callbacks[name]=_G[name] end
 local oldsource=prior.source
 local config={}
 for k,v in pairs(prior.config) do if k~='run_slot' and k~='receive' then config[k]=v end end
 local function recover(message)
  for _,name in ipairs(names) do _G[name]=callbacks[name] end
  _G.seedsow_editor=parent
  prior.closed=false;prior.running=false;prior.user_update=nil
  parent.start(engine,config,oldsource)
  error('Side editor could not start; original editor restored: '..tostring(message),0)
 end
 local ok,module=pcall(chunk)
 if not ok or type(module)~='table' or type(module.start)~='function' then recover(module) end
 prior.closed=true;prior.running=false;prior.user_update=nil
 _G.seedsow_editor=module
 local started,why=pcall(module.start,engine,{build_id='BUILD_ID',isolated=true,side_slot=SIDE_SLOT},source)
 if not started then recover(why) end
end
'''
    # All placeholders are fixed trusted builder values. Replace patch last so
    # ordinary source text inside the patch is never treated as a placeholder.
    start=start.replace(b'BASE_CRC',str(zlib.adler32(base)).encode())
    start=start.replace(b'SOURCE_SIZE',str(len(updated)).encode()).replace(b'SOURCE_CRC',str(zlib.adler32(updated)).encode())
    start=start.replace(b'BUILD_ID',build_id.encode()).replace(b'SIDE_SLOT',str(slot).encode())
    return start.replace(b'PATCH_DATA',patch)

def build_update(base_save,slot=30,output=None,source=None,include_save=False):
    """Build an upload, optionally adding a fresh slot to a copy of the backup."""
    candidate=current_source() if source is None else source
    updated=isolated_source(candidate,slot)
    base_save=Path(base_save).resolve()
    files=load_backup(base_save)
    if 'ssedit1.lua' not in files:
        raise ValueError('An installed editor backup with ssedit1.lua is required.')
    base=files['ssedit1.lua']
    program_name=f'editor-update-{slot:03d}.lua'
    additions={}
    if include_save:
        required=(f'ssseed{slot:03d}.bin',f'ss{slot:03d}.asb')
        if any(name not in files for name in required):
            raise ValueError('Missing installed launcher for the update slot.')
        additions={program_name:b'',f'ssslot{slot:03d}.ref':(program_name+'\n').encode(),
                   f'save{slot:04d}.dat':files[required[0]],
                   f'save{slot:04d}.png':files['save0001.png'],
                   f'save{slot:04d}_s.png':files['save0001_s.png']}
        occupied=files.keys() & additions.keys()
        if occupied:
            raise ValueError('Update slot or filename already in use: '+', '.join(sorted(occupied)))
    build_id=secrets.token_hex(4)
    program=payload(base,updated,slot,build_id)
    out=Path(output) if output else ROOT/'build/side-editor'/build_id
    out=out.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError('Output directory must be empty. Choose a new output folder.')
    out.mkdir(parents=True,exist_ok=True)
    target=out/f'Editor-Update-slot-{slot}.lua'
    target.write_bytes(program)
    manifest={'build_id':build_id,'base_save':str(base_save),'base_core_adler32':zlib.adler32(base),
        'slot':slot,'lua_file':str(target),'upload_bytes':len(program),
        'reconstructed_bytes':len(updated),'source_adler32':zlib.adler32(updated),
        'program_sha256':hashlib.sha256(program).hexdigest(),'private_prefix':f'ed{slot:03d}-',
        'original_core_repair_disabled':True,'independent_loader':False,'hardware_tested':False}
    if include_save:
        additions[program_name]=program
        save_target=out/'Seedsow-Lua-Editor-Update-Save.zip'
        with zipfile.ZipFile(save_target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
            for name,data in sorted((files | additions).items()):
                info=zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=0o100644 << 16
                archive.writestr(info,data)
        with zipfile.ZipFile(save_target) as archive:
            assert archive.testzip() is None
            assert all(archive.read(name)==data for name,data in (files | additions).items())
        manifest.update(save_zip=str(save_target),save_sha256=hashlib.sha256(save_target.read_bytes()).hexdigest(),
                        original_files_preserved=len(files),save_files=len(files)+len(additions))
        (out/(save_target.name+'.sha256')).write_text(manifest['save_sha256']+'  '+save_target.name+'\n')
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (out/(target.name+'.sha256')).write_text(manifest['program_sha256']+'  '+target.name+'\n')
    instructions=f'''Seedsow Lua Editor - current development build / slot {slot}

Editor-Update-slot-{slot}.lua is a console Lua program.
Upload it through your existing Pi uploader to UNUSED user slot {slot},
or enter the complete source in the console editor. Save + publish,
then load slot {slot}. It must be published to this exact slot.
Keep the installed editor and recovery slots 1-3.

The header must say LUA EDITOR / update slot {slot}.
Line up/down moves the cursor, preserving the preferred byte column.
Scroll up/down and Page up/down browse without moving the cursor.
[|] marks the insertion point and is not part of the source.
A activates; B backspaces/returns; X types; Y runs; L/R move a byte.
Normal controls work immediately. A saved calibration takes precedence.
Settings and reports use ed{slot:03d}- names.

This build still depends on the retained base loader and recovery core.
Console testing is pending. Automated results are in local-checks.json
when tests/check_side_editor.py has been run against this directory.
'''
    if include_save:
        instructions+='''
Seedsow-Lua-Editor-Update-Save.zip is a complete restoreable save.
Back up your current game save before restoring it with JKSV on Switch 1.
Transfer to Switch 2 if needed. Load slot 1 once to register the new entry,
choose Title screen, then load the update slot shown above.
The input backup's files are retained byte-for-byte in this ZIP.
Use the Lua upload option above to retain programs on your console that
are absent from that input backup.
'''
    (out/'README.txt').write_text(instructions,encoding='utf-8')
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',type=Path,required=True,help='Current editor backup ZIP')
    p.add_argument('--slot',type=int,default=30)
    p.add_argument('--output',type=Path,help='New or empty output directory')
    p.add_argument('--source',type=Path,help='Optional combined candidate source, before slot binding')
    p.add_argument('--include-save',action='store_true',help='Also copy the backup and install the update in a fresh slot')
    args=p.parse_args()
    manifest=build_update(args.base,args.slot,args.output,
                          args.source.read_bytes() if args.source else None,args.include_save)
    print(json.dumps(manifest,indent=2))

if __name__=='__main__':main()
