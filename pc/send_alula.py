#!/usr/bin/env python3
"""Send Alula v1 to the uploader running in an existing Seedsow editor.

The Switch uploader's TARGET_SLOT setting is authoritative; the PC does not pick
or overwrite a user slot. Nothing alters game startup, saveg.dat or system.dat.
The public alula v1 release is downloaded by this script unless --release is given.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import secrets
import socket
import struct
import sys
import urllib.request
import zipfile
import zlib

RELEASE_URL = 'https://github.com/alula/switch-artemis-launcher/releases/download/v1/seedsow_save.zip'
RELEASE_SHA256 = 'd9f3d0204860aa9764106c54b18d2b226dd525d72fbfea6bd7a706e9cfeef76e'
ROOT = Path(__file__).resolve().parent.parent


def load_release(path):
    if path is not None:
        if Path(path).stat().st_size > 2*1024*1024:
            raise ValueError('Unexpectedly large alula release ZIP')
        raw = Path(path).read_bytes()
    else:
        print('PC: downloading alula v1 Seedsow launcher...',flush=True)
        req = urllib.request.Request(RELEASE_URL,headers={'User-Agent':'Seedsow-Artemis-Sidecar/1.0'})
        with urllib.request.urlopen(req,timeout=40) as response:
            raw = response.read(2*1024*1024 + 1)
    if len(raw)>2*1024*1024:
        raise ValueError('Unexpectedly large alula release ZIP')
    if hashlib.sha256(raw).hexdigest() != RELEASE_SHA256:
        raise ValueError('Release checksum mismatch. Use the original Alula v1 seedsow_save.zip; '
                         'this installer does not support a different release or a repacked ZIP.')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        needed=['core.lua','http.lua','inject.lua','exploita.lua','proggy.ttf']
        members={}
        for entry in z.infolist():
            name=entry.filename.replace('\\','/').split('/')[-1]
            if entry.is_dir() or name not in needed:
                continue
            if name in members:
                raise ValueError('Ambiguous release member: '+name)
            if not 0 < entry.file_size <= 65536:
                raise ValueError('Unexpected release file size: '+name)
            members[name]=entry
        for n in needed:
            if n not in members: raise ValueError('Alula v1 release missing '+n)
        return {n:z.read(members[n]) for n in needed}


def one(src,old,new,name):
    count=src.count(old)
    if count!=1: raise ValueError(f'Unexpected alula {name}: required pattern found {count} times: {old[:80]!r}')
    return src.replace(old,new)


def prepare_files(release):
    inject=release['inject.lua'].decode('utf-8')
    for old,new in (
      ('local is_recovery = false','local is_recovery = _G.n2h_was_recovery or false'),
      ('[!] Ignored launcher update. Press - again to enable recovery mode for payloads.',
       '[!] Recovery: using original launcher, core and payload files.'),
      ('save:/proggy.ttf','save:/ax_proggy.ttf'),
      ('local updated_payload = "save:/" .. mode .. "2.lua"','local updated_payload = "save:/ax_" .. mode .. "2.lua"'),
      ('local payload = "save:/" .. mode .. ".lua"','local payload = "save:/ax_" .. mode .. ".lua"'),
      ('local core_path = "save:/core.lua"','local core_path = "save:/ax_core.lua"'),
      ('local updated_core_path = "save:/core2.lua"','local updated_core_path = "save:/ax_core2.lua"'),
    ):
        inject=one(inject,old,new,'inject.lua')
    http=release['http.lua'].decode('utf-8')
    for old in ('core.lua','inject.lua','http.lua','proggy.ttf'):
        http=http.replace('save:/'+old,'save:/ax_'+old)
    http=one(http,'\t["save:/saveg.dat"] = true,',
        '\t["save:/saveg.dat"] = true,\n'
        '\t["save:/inject.iet"] = true,\n'
        '\t["save:/save9999.dat"] = true,\n'
        '\t["save:/ssedit1.lua"] = true,\n'
        '\t["save:/ssedit2.lua"] = true,\n'
        '\t["save:/ssedit3.lua"] = true,','http.lua')
    sidecar=(Path(__file__).parent/'Artemis_Sidecar.lua').read_bytes()
    files=[
        ('ax_core.lua',release['core.lua']),
        ('ax_http.lua',http.encode('utf-8')),
        ('ax_inject.lua',inject.encode('utf-8')),
        ('ax_exploita.lua',release['exploita.lua']),
        ('ax_proggy.ttf',release['proggy.ttf']),
        ('__SIDECAR__',sidecar),
    ]
    for name,data in files:
        if not 0<len(data)<=65536:raise ValueError(name+' exceeds receiver 65536-byte limit')
    return files


def adler(data):
    return zlib.adler32(data)&0xffffffff


def stage_lua(files, run_id):
    # This script is streamed as the first packet after the receiver connects.
    # The five alula files and sidecar follow separately as u32-length packets.
    entries='{' + ','.join('{'+json.dumps(n)+','+str(len(b))+','+str(adler(b))+'}' for n,b in files) + '}'
    template=r'''-- Artemis sidecar installer. The uploader passes TARGET_SLOT here.
local rx,ed,slot,eng=...
local meta=__ENTRIES__
local notes={"ARTEMIS_INSTALL_BEGIN RUN=__RUN_ID__"}
local function note(s)notes[#notes+1]=s end
local function u32()
 local a,b,c,d=rx(4):byte(1,4)
 assert(a and d,"truncated file length")
 return a+b*256+c*65536+d*16777216
end
local function adler(data)
 local a,b=1,0
 for i=1,#data do a=(a+data:byte(i))%65521;b=(b+a)%65521 end
 return b*65536+a
end
local function exists(name)
 local ok,v=pcall(function()return eng:isFileExists("save:/"..name)end)
 if not ok then error("Cannot check existing file "..name)end
 return v==true or v==1
end
local function read(name)
 return ed.read(name)
end
local function check(name,data)
 if exists(name)then
  local old=read(name)
  if old~=data then error("COLLISION "..name.."; no files were installed")end
 end
end
local function put(name,data)
 if exists(name)then note("KEPT "..name);return end
 assert(ed.write(name,data),"WRITE "..name)
 assert(read(name)==data,"READBACK "..name)
 note("SAVED "..name.." "..#data)
end
local ok,reason=pcall(function()
 assert(type(slot)=="number" and slot%1==0 and slot>=4 and slot<=120,"Invalid TARGET_SLOT")
 local sn=string.format("%03d",slot)
 local prefix=string.format("save%04d",slot)
 local source="ax_slot"..sn..".lua"
 local ref="ssslot"..sn..".ref"
 local seedname="ssseed"..sn..".bin"
 assert(exists("ss"..sn..".asb"),"Missing editor bootstrap for slot "..sn)
 local seed=assert(read(seedname),"Missing slot template "..seedname)
 local thumb=assert(read("ssethumb.png"),"Missing editor thumbnail")
 local desired={
  {prefix..".dat",seed},
  {prefix..".png",thumb},
  {prefix.."_s.png",thumb},
  {ref,source.."\n"}
 }
 -- Refuse an existing published slot, even if it belongs to another user.
 for _,entry in ipairs(desired)do
  if exists(entry[1])then error("SLOT_IN_USE "..slot.." "..entry[1].."; no files installed")end
 end
 if exists(source)then error("SOURCE_IN_USE "..source.."; no files installed")end
 local received={}
 for i,record in ipairs(meta)do
  local n=u32()
  assert(n==record[2] and n<=65536,"Wrong file length: "..record[1])
  local data=rx(n)
  assert(#data==n and adler(data)==record[3],"Damaged file: "..record[1])
  received[i]=data
  note("RX "..record[1].." "..n)
 end
 for i,record in ipairs(meta)do
  if record[1]~="__SIDECAR__"then check(record[1],received[i])end
 end
 -- All preflight checks completed before any installer file is written.
 for i,record in ipairs(meta)do
  if record[1]~="__SIDECAR__"then put(record[1],received[i])end
 end
 put(source,received[#meta])
 for i=1,3 do put(desired[i][1],desired[i][2])end
 -- Commit the slot reference LAST. The standard editor repairs menu metadata
 -- on its next load; no raw modification to saveg.dat or system.dat needed.
 put(ref,desired[4][2])
 note("ARTEMIS_INSTALL_COMPLETE SLOT="..slot.." RUN=__RUN_ID__")
end)
if not ok then note("ARTEMIS_INSTALL_FAILED "..tostring(reason))end
ed.write("ax_install.log",table.concat(notes,"\n").."\n")
'''
    if not run_id or any(c not in '0123456789abcdef' for c in run_id):
        raise ValueError('Invalid install run ID')
    return template.replace('__ENTRIES__',entries).replace('__RUN_ID__',run_id)


def write_build(files,stage,out,run_id):
    out.mkdir(parents=True,exist_ok=True)
    (out/'stage1_install.lua').write_bytes(stage)
    (out/'sender-manifest.json').write_text(json.dumps({
        'purpose':'Manual-launch Artemis sidecar; no startup changes',
        'run_id':run_id,
        'upstream_release':RELEASE_URL,
        'upstream_sha256':RELEASE_SHA256,
        'files':[{'name':n,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()} for n,data in files],
        'destination_slot':'configured on Switch: TARGET_SLOT',
        'DO_NOT_OVERWRITE':['saveg.dat','system.dat','autosave.dat','inject.iet','save9999.dat','existing user slots'],
    },indent=2)+'\n',encoding='utf-8')


def serve(stage,files,bind,port):
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        server.bind((bind,port))
        server.listen(1)
        print(f'Listening at {bind}:{port}. Now run the uploader from its editor slot.\n'
              'Keep this window open. Ctrl+C cancels the sender.',flush=True)
        conn,addr=server.accept()
        with conn:
            conn.settimeout(30)
            print('Switch connected:',addr,flush=True)
            conn.sendall(struct.pack('<I',len(stage))+stage)
            print('Sent installer stage:',len(stage),'bytes',flush=True)
            total=sum(len(data) for _,data in files)
            sent=0
            for name,data in files:
                conn.sendall(struct.pack('<I',len(data))+data)
                sent+=len(data)
                print(f'Sent {name:19s} {len(data):6d} bytes  ({sent}/{total})',flush=True)
            print('Transmission finished. On the console, open ax_install.log in the editor and '
                  'check ARTEMIS_INSTALL_COMPLETE and the run ID printed above. See docs/02-existing-editor.md.',flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,help='Generated config.json (default: build/config.json when --port is omitted)')
    p.add_argument('--release',type=Path,help='Alula v1 seedsow_save.zip on this PC (omit to download)')
    p.add_argument('--listen',help='PC listen address (default: configured PC IP, or 0.0.0.0 with explicit --port)')
    p.add_argument('--port',type=int,help='Must match PC_PORT; normally read from generated config.json')
    p.add_argument('--out',type=Path,default=ROOT/'build',help='Local installer and manifest output directory')
    p.add_argument('--prepare-only',action='store_true')
    args=p.parse_args()
    config={}
    if args.config is not None or args.port is None:
        config_path=args.config or ROOT/'build/config.json'
        if not config_path.is_file():
            p.error('Run tools/make_sheet.py first, or use --config PATH or --port PORT.')
        config=json.loads(config_path.read_text('utf-8'))
        if not isinstance(config,dict) or config.get('version')!='seedsow-artemis-installer-1':
            p.error('Expected an Artemis installer config.json generated by tools/make_sheet.py.')
        if type(config.get('port')) is not int or not isinstance(config.get('pc_ip'),str):
            p.error('Invalid port or computer IP in config.json. Generate the settings again.')
        if args.port is not None and args.port!=config['port']:
            p.error('--port differs from config.json. Regenerate the uploader when changing its port.')
        args.port=config['port']
    args.listen=args.listen or config.get('pc_ip','0.0.0.0')
    if not 1 <= args.port <= 65535:
        p.error('--port must be in 1..65535')
    files=prepare_files(load_release(args.release))
    run_id=secrets.token_hex(4)
    stage=stage_lua(files,run_id).encode('utf-8')
    write_build(files,stage,args.out,run_id)
    if args.prepare_only:
        print('Prepared',len(files),'files; install stage',len(stage),'bytes in',args.out)
        return
    print(f'Install run ID: {run_id}. Expected log: ARTEMIS_INSTALL_COMPLETE SLOT=<launcher slot> RUN={run_id}',flush=True)
    if config:
        print(f"Uploader slot: {config.get('uploader_slot')}; launcher destination: {config.get('launcher_slot')}",flush=True)
    serve(stage,files,args.listen,args.port)

if __name__=='__main__':
    try:main()
    except (OSError,ValueError,AssertionError,zipfile.BadZipFile) as ex:
        print('ERROR:',str(ex),file=sys.stderr)
        print('If the console uploader was already running, close Seedsow before trying again.\n'
              'Check docs/05-troubleshooting.md; do not assume a partial send completed the install.',file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit('\nSender stopped. If the console uploader was running, close Seedsow before retrying.')
