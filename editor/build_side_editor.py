"""Build a published Lua editor update without replacing the V3 recovery core."""
import argparse
import difflib
import hashlib
import importlib.util
import json
import secrets
import sys
import zipfile
import zlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def current_source():
    spec=importlib.util.spec_from_file_location('seedsow_editor_builder',HERE/'build.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.core_source()

def literal(data):
    for n in range(1,20):
        eq=b'='*n
        if b']'+eq+b']' not in data:
            # Prefix with a sentinel so Lua's long-string newline handling never
            # strips an inserted first newline from a patch.
            return b'(['+eq+b'[!'+data+b']'+eq+b']):sub(2)'
    raise ValueError('Cannot delimit source')

def replace_once(source,before,after):
    assert source.count(before)==1,repr(before)
    return source.replace(before,after)

def isolated_source(source,slot):
    prefix=f'ed{slot:03d}-'.encode()
    source=source.replace(b'ssedit-',prefix)
    source=replace_once(source,b'local function repair()\n',
        b'local function repair()\n    if S.config.isolated then return 0 end -- V3 recovery files are not this version\'s repair targets.\n')
    source=replace_once(source,b'function Editor.start(engine,config,source)\n',
        b'function Editor.start(engine,config,source)\n    assert(config and config.isolated and config.side_slot=='+str(slot).encode()+b',"Use this editor through its side-loader")\n')
    source=replace_once(source,b'    assert(W.valid(name),\'Invalid filename\')\n',
        b'''    assert(W.valid(name),'Invalid filename')
    local lower=name:lower()
    if lower=='saveg.dat' or lower:sub(1,6)=='ssedit' or lower:match('^save000[123]%.') or lower:match('^sed0[123]%.asb') or lower:match('^ssboot[123]%.bin') or lower:match('^ssseed00[123]%.bin') then
        return false,'Original V3 recovery file is read-only in this editor'
    end
''')
    source=replace_once(source,b"{'ssedit','ssseed'",b"{'"+prefix+b"','ssedit','ssseed'")
    source=replace_once(source,b'local function publish()\n',
        b'local function publish()\n    assert(S.slot~=S.config.side_slot,"This slot holds the running side editor; publish to another user slot")\n')
    own=b"W.read(S.base,'"+prefix+b"controls.txt')"
    source=replace_once(source,b'Input.new(engine,'+own+b')',
        b"Input.new(engine,"+own+b" or W.read(S.base,'ssedit-controls.txt'))")
    source=replace_once(source,b"if not c.draw_at or now-c.draw_at>=150 then",
        b"if c.done or not c.draw_at or now-c.draw_at>=150 then")
    source=replace_once(source,b'SEEDSOW LUA EDITOR V3 / protected entry slots 1, 2, 3',
        f'LUA EDITOR UPDATE / slot {slot} / recovery: 1, 2, 3'.encode())
    source=replace_once(source,b"say('Repaired '..repair()..' editor files; all three entry slots registered')",
        b"say('Side editor ready; original recovery copies were left untouched ('..repair()..' repairs)')")
    for suffix in ('frame','key','event','keyboard_returned'):
        source=source.replace(('seedsow_editor_'+suffix).encode(),('seedsow_side_%03d_'%slot+suffix).encode())
    return source

def payload(base,updated,slot,build_id):
    nodes=[]
    oldlines=base.splitlines(keepends=True);newlines=updated.splitlines(keepends=True)
    offsets=[0]
    for line in oldlines:offsets.append(offsets[-1]+len(line))
    for tag,a,b,c,d in difflib.SequenceMatcher(None,oldlines,newlines,autojunk=False).get_opcodes():
        if tag=='equal':nodes.append(('{%d,%d}'%(offsets[a]+1,offsets[b])).encode())
        elif tag in ('replace','insert'):nodes.append(b'('+literal(b''.join(newlines[c:d]))+b')')
    patch=b'{'+b',\n'.join(nodes)+b'}'
    prefix=f'ed{slot:03d}-'
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

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',type=Path,required=True,help='Current editor backup ZIP')
    p.add_argument('--slot',type=int,default=30)
    p.add_argument('--output',type=Path,default=ROOT/'build/side-editor')
    p.add_argument('--source',type=Path,help='Optional updated combined editor core; recovery files still use --base')
    args=p.parse_args()
    if args.slot not in range(4,121):raise ValueError('Choose a user slot 4-120')
    with zipfile.ZipFile(args.base) as z:base=z.read('ssedit1.lua')
    candidate=args.source.read_bytes() if args.source else current_source()
    updated=isolated_source(candidate,args.slot)
    build_id=secrets.token_hex(4);program=payload(base,updated,args.slot,build_id)
    out=args.output/build_id;out.mkdir(parents=True)
    target=out/f'Editor-Update-slot-{args.slot}.lua';target.write_bytes(program)
    manifest={'build_id':build_id,'base_save':str(args.base.resolve()),'base_core_adler32':zlib.adler32(base),
        'slot':args.slot,'lua_file':str(target.resolve()),'upload_bytes':len(program),
        'reconstructed_bytes':len(updated),'source_adler32':zlib.adler32(updated),
        'program_sha256':hashlib.sha256(program).hexdigest(),'private_prefix':f'ed{args.slot:03d}-',
        'original_core_repair_disabled':True,'independent_loader':False,'hardware_tested':False}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (out/'README.txt').write_text(f'''Editor update for slot {args.slot}
Keep the installed editor and recovery slots 1-3.
This is an ordinary Lua file, not an installation save ZIP.
Use the console editor to enter it manually, or use the optional Pi uploader.
Save and publish it to user slot {args.slot}, then load that slot.
Settings and reports use ed{args.slot:03d}- names.
The update still depends on the retained base loader and recovery core.
Local startup/recovery checks pass; console testing of this update is pending.
''',encoding='utf-8')
    print(json.dumps(manifest,indent=2))

if __name__=='__main__':main()
