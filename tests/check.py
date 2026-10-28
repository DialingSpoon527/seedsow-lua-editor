"""Validate editor packaging and exercise its actual Lua with a controlled engine.

Native UI/Pluto/commit behavior is a stand-in; hardware results are not inferred.
"""
import argparse
import hashlib
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'editor'),str(ROOT/'pc'),str(ROOT/'pi')]
from lupa.lua51 import LuaRuntime, LuaError
from indexed_save import IndexedSave
from asb import decode_asb
from save_globals import read_globals


class Console:
    def __init__(self,files,directory,metadata=None):
        self.directory=directory
        self.initial=files
        self.metadata=metadata
        self.lua=LuaRuntime(encoding=None,unpack_returned_tuples=True)
        self.engine=self.lua.table()
        self.variables={}
        self.clock=1000
        self.writes=[]
        self.edges=set()
        self.held=set()
        self.point=(-1,-1)
        self.touch=0
        self.handlers={}
        self.event_handlers={}
        self.filter=None
        self.pending=[]
        self.modal=None
        self.denied=set()
        self.messages={}
        self.layers={}
        self.shapes={}
        self.message_id=None
        if not directory.exists():directory.mkdir()
        for name,data in files.items():
            (directory/name).write_bytes(data)
        self.lua.globals()[b'__open']=self.io_open
        self.lua.globals()[b'__metadata']=self.persist
        self.lua.execute(b'io.open=function(p,m) return __open(p,m) end; pluto={persist=function(_,v) return __metadata(v) end}; game={savemax=120,sw=true}; init={save_column=6}; csv={advkey={def={}}}; sys={saveslot={}}')
        if metadata:
            self.lua.globals()[b'sys']=self.table(metadata)
        e=self.engine
        e[b'tag']=self.tag
        e[b'file']=lambda _,p:self.path(p).read_bytes()
        e[b'var']=lambda _,name:b'save:' if name==b's.savepath' else self.variables.get(name,b'0')
        e[b'now']=lambda _:self.clock
        e[b'isFileExists']=lambda _,p:self.path(p).exists()
        e[b'setEventHandler']=lambda _,p:self.event_handlers.update(dict(p.items()))
        e[b'setEventFilter']=self.set_filter
        e[b'getTouchCount']=lambda _:self.touch
        e[b'getMousePoint']=lambda _:self.lua.table_from({b'x':self.point[0],b'y':self.point[1]})
        e[b'isDownEdge']=lambda _,key:key in self.edges
        e[b'isDown']=lambda _,key:key in self.held

    def table(self,value):
        if isinstance(value,dict):return self.lua.table_from({k:self.table(v) for k,v in value.items()})
        return value

    def persist(self,value):
        def convert(v):
            if hasattr(v,'items'):return {k:convert(item) for k,item in v.items()}
            return v
        self.metadata=convert(value)
        return b'STAND-IN PLUTO METADATA'

    def path(self,name):
        assert name.startswith(b'save:/'),name
        plain=name[6:].decode('ascii')
        assert plain and '/' not in plain and '\\' not in plain and plain not in ('.','..'),plain
        return self.directory/plain

    def io_open(self,name,mode):
        target=self.path(name)
        if mode in (b'wb',b'ab') and target.name in self.denied:return None,b'Simulated write refusal'
        try:f=target.open(mode.decode())
        except OSError as error:return None,str(error).encode()
        if mode in (b'wb',b'ab'):self.writes.append(target.name)
        obj=self.lua.table()
        obj[b'read']=lambda _,count:f.read(int(count)) or None
        obj[b'write']=lambda _,data:(f.write(data) and obj) if data else obj
        obj[b'flush']=lambda _:(f.flush() or True)
        obj[b'close']=lambda _:(f.close() or True)
        return obj

    def set_filter(self,_,fn):self.filter=fn

    @staticmethod
    def measure_width(value,size=20):
        widths={ord('W'):18,ord('i'):4,ord(' '):5,ord('|'):4,ord('['):6,ord(']'):6}
        return sum(widths.get(byte,10) for byte in value)*size/20

    def tag(self,_,p):
        row=dict(p.items()); name=row[1]
        assert name not in (b'httpget',b'httppost',b'file',b'callnative'),name
        if name==b'var':
            if row.get(b'system')==b'get_message_layer_width':
                width=self.measure_width(self.messages[self.message_id],self.layers[self.message_id][b'size'])
                self.variables[row[b'name']]=str(width).encode()
            else:self.variables[row[b'name']]=row[b'data']
        elif name==b'save':
            assert re.fullmatch(rb'(?:ssedit|ed\d{3})-commit[.]dat',row[b'file'])
            (self.directory/row[b'file'].decode('ascii')).write_bytes(b'STAND-IN NATIVE COMMIT')
        elif name==b'jump':self.pending.extend(decode_asb(self.path(row[b'file']).read_bytes()))
        elif name==b'setonpush':self.handlers[int(row[b'key'])]=row[b'function']
        elif name==b'delonpush':self.handlers.pop(int(row[b'key']),None)
        else:
            assert name in (b'chgmsg',b'fontinit',b'font',b'rp',b'print',b'/chgmsg',b'lyprop',b'lydel',b'lyc',b'autosave',b'skip',b'automode',b'flip',b'keyconfig',b'reset'),name
            if name==b'chgmsg':
                self.message_id=row[b'id']
                self.layers.setdefault(self.message_id,{})
            elif name==b'font' and self.message_id:
                self.layers[self.message_id].update({k:int(row[k]) for k in (b'width',b'height',b'size')})
            elif name==b'lyc':
                self.shapes[row[b'id']]=dict(row)
            elif name==b'lydel':
                for items in (self.layers,self.messages,self.shapes):
                    for key in list(items):
                        if key==row[b'id'] or key.startswith(row[b'id']+b'.'):del items[key]
            elif name==b'lyprop' and row[b'id'] in self.layers:
                self.layers[row[b'id']].update({k:int(row[k]) for k in (b'left',b'top',b'visible') if k in row})
            elif name==b'lyprop' and row[b'id'] in self.shapes:
                self.shapes[row[b'id']].update(row)
            elif name==b'rp' and self.message_id:self.messages[self.message_id]=b''
            elif name==b'print' and self.message_id:
                self.messages[self.message_id]=self.messages.get(self.message_id,b'')+row[b'data']

    def load(self,slot):
        native=IndexedSave((self.directory/f'save{slot:04d}.dat').read_bytes())
        caret=native.groups[native.groups[0][3]]
        commands=decode_asb(self.path(native.lp(caret[3])).read_bytes())
        self.lua.execute(commands[0][2]['script'].encode())
        self.lua.globals()[commands[1][2]['function'].encode()](self.engine)
        self.module=self.lua.globals()[b'seedsow_editor']
        self.frame()

    def state(self):return self.module[b'test_state']()
    def action(self,name,value=None):
        return self.module[b'test_action'](name.encode(),value.encode() if isinstance(value,str) else value)

    def frame(self):
        self.clock+=200
        while self.pending and not self.modal:
            command,_,args=self.pending.pop(0)
            if command=='dialog':self.modal=args
            elif command=='calllua':self.lua.globals()[args['function'].encode()]()
        callback=self.event_handlers.get(b'onEnterFrame',b'seedsow_editor_frame')
        if callback:self.lua.globals()[callback]()
        self.edges=set()

    def key(self,code):
        self.held.add(code)
        self.edges.add(code)
        row=self.lua.table_from({b'key':str(code).encode()})
        if self.filter:self.filter(self.engine,b'setonpush',row)
        if code in self.handlers:self.lua.globals()[self.handlers[code]](self.engine,row)
        self.frame()
        self.held.clear(); self.frame(); self.frame()

    def reply(self,value):
        self.frame()
        assert self.modal,'No native keyboard request'
        value=value.decode('utf-8') if isinstance(value,bytes) else value
        self.variables[self.modal['textfield'].encode()]=value[:32].encode('utf-8')
        self.modal=None
        self.frame()

    def prompt(self,button,value):
        # Model repeated manual Keyboard + insertions, not a larger native dialog.
        if button=='keyboard' and len(value)>32:
            if self.state()[b'hex']:
                value=''.join(value.split())
            for start in range(0,len(value),32):
                self.action(button)
                self.reply(value[start:start+32])
            return
        self.action(button)
        self.reply(value)


def expect_error(fn,text):
    try:fn()
    except LuaError as error:
        assert text in str(error),(text,str(error))
    else:raise AssertionError('Expected rejection: '+text)


def check(run):
    manifest=json.loads((run/'manifest.json').read_text())
    version=manifest.get('version',1)
    with zipfile.ZipFile(run/'Seedsow-Lua-Editor-Save.zip') as archive:
        assert archive.testzip() is None
        files={name:archive.read(name) for name in archive.namelist()}
    assert set(files)==set(manifest['save_files'])
    for name,data in files.items():
        assert hashlib.sha256(data).hexdigest()==manifest['save_files'][name]
        folder=run/f'Seedsow - Lua Editor V{version}'
        if folder.exists():assert (folder/name).read_bytes()==data
    values=read_globals(files['saveg.dat'])
    if manifest['entry_label']:
        assert manifest['entry_label'].encode() in values['g.system']
    if version>=3:
        files['ssedit-controls.txt']=b'A isDown 258\nB isDown 257\nX isDown 259\nY isDown 256\nL isDown 260\nR isDown 261\n'
    for slot in range(1,121):
        native=IndexedSave(files[f'ssseed{slot:03d}.bin'])
        caret=native.groups[native.groups[0][3]]
        name=f'sed{slot:02d}.asb' if slot<=3 else f'ss{slot:03d}.asb'
        assert native.lp(caret[3])==('save:/'+name).encode()
        commands=decode_asb(files[name])
        assert commands[1][2]['function']==f'seedsow_editor_boot_{slot:03d}'
        if slot>=4:assert ('run_slot='+str(slot)) in commands[0][2]['script']
    with tempfile.TemporaryDirectory(dir=HERE) as temporary:
        base=Path(temporary)
        c=Console(files,base/'initial')
        c.load(1)
        assert c.state()[b'slot']==4
        keys=[b[b'value'] for _,b in c.state()[b'buttons'].items() if b[b'name']==b'key']
        assert set(bytes([i]) for i in range(32,127)) <= set(keys)
        assert b'\n' in keys and b'\t' in keys and b'BS' in keys
        assert all(c.metadata[b'saveslot'][i][b'file']==f'save{i:04d}'.encode() for i in (1,2,3,4))
        assert all(c.metadata[b'saveslot'][b'lock'][i] is True for i in (1,2,3))
        assert c.metadata[b'saveslot'][b'count']>=4
        assert all(c.metadata[b'saveslot'][b'check'][f'save{i:04d}'.encode()] is True for i in (1,2,3,4))
        w=c.module[b'storage']
        # Two copies can fail; the third bootstraps and restores the damaged code.
        disk={p.name:p.read_bytes() for p in c.directory.iterdir()}
        disk['ssedit1.lua']=b'broken source'; disk['ssedit3.lua']=b''
        c=Console(disk,base/'fallback',c.metadata); c.load(3)
        assert (c.directory/'ssedit1.lua').read_bytes()==files['ssedit1.lua']
        assert (c.directory/'ssedit3.lua').read_bytes()==files['ssedit3.lua']
        # Keyboard uses a real, decoded ASB command and completion callback.
        c.prompt('slot','12')
        c.state()[b'buffer']=b''; c.state()[b'saved']=b''; c.state()[b'cursor']=0
        c.prompt('keyboard','print("PERSISTENT SLOT TWELVE")\n')
        assert c.state()[b'buffer']==b'print("PERSISTENT SLOT TWELVE")\n'
        c.action('publish')
        assert (c.directory/'sscode012.lua').read_bytes()==c.state()[b'buffer']
        assert (c.directory/'save0012.dat').read_bytes()==files['ssseed012.bin']
        assert c.metadata[b'saveslot'][12][b'file']==b'save0012'
        saved={p.name:p.read_bytes() for p in c.directory.iterdir()}
        fresh=Console(saved,base/'restarted',c.metadata); fresh.load(12)
        assert fresh.state()[b'running'] is True
        assert fresh.state()[b'output'][1]==b'PERSISTENT SLOT TWELVE', (dict(fresh.state()[b'output'].items()),fresh.state()[b'status'],fresh.state()[b'buffer'])
        fresh.key(257); assert fresh.state()[b'running'] is False
        # Full binary range, cursor offsets, replacement, recovery and literal raw saves.
        fresh.state()[b'saved']=fresh.state()[b'buffer']
        fresh.prompt('filename','bytes.bin')
        fresh.action('hex')
        all_bytes=bytes(range(256))
        fresh.prompt('keyboard',all_bytes.hex(' '))
        assert fresh.state()[b'buffer']==all_bytes
        fresh.action('save')
        assert (fresh.directory/'bytes.bin').read_bytes()==all_bytes
        fresh.prompt('offset','0'); fresh.action('patch'); fresh.prompt('keyboard','FE ED 00 FF')
        assert fresh.state()[b'buffer']==b'\xfe\xed\x00\xff'+all_bytes[4:]
        fresh.action('save')
        assert (fresh.directory/'bytes.bin.bak').read_bytes()==all_bytes
        fresh.action('restore'); assert fresh.state()[b'buffer']==all_bytes
        fresh.action('undo'); assert fresh.state()[b'buffer']!=all_bytes
        # Editor files and index stay protected; raw non-editor native slots remain writable.
        w=fresh.module[b'storage']
        for name in ('save0001.dat','save0002.dat','save0003.dat','saveg.dat','ssedit1.lua','sed01.asb','ssseed012.bin','ss012.asb','ssboot1.bin'):
            result=w[b'save'](b'save:',name.encode(),b'damage')
            assert result[0] is False,name
        assert w[b'save'](b'save:',b'save0020.dat',b'\x00RAW\xff') is True
        assert (fresh.directory/'save0020.dat').read_bytes()==b'\x00RAW\xff'
        assert not w[b'valid'](b'../outside') and not w[b'valid'](b'sdmc:/test')
        expect_error(lambda:w[b'unhex'](b'abc'),'two digits')
        expect_error(lambda:w[b'unhex'](b'GG'),'only 0-9')
        # Failed staging/backup never proceeds to target replacement.
        assert w[b'save'](b'save:',b'failure.txt',b'old') is True
        fresh.denied.add('failure.txt.new')
        assert w[b'save'](b'save:',b'failure.txt',b'new')[0] is False
        assert (fresh.directory/'failure.txt').read_bytes()==b'old'
        fresh.denied.clear(); fresh.denied.add('failure.txt.bak')
        assert w[b'save'](b'save:',b'failure.txt',b'new')[0] is False
        assert (fresh.directory/'failure.txt').read_bytes()==b'old'
        fresh.denied.clear()
        # Actual queued/polled controls coalesce one physical press into one action.
        fresh.state()[b'buffer']=b''; fresh.state()[b'saved']=b''; fresh.state()[b'cursor']=0
        fresh.state()[b'hex']=False
        fresh.state()[b'focus']=next(i for i,b in fresh.state()[b'buttons'].items() if b[b'name']==b'key' and b[b'value']==b'a')
        fresh.frame(); fresh.frame() # Let the modal-keyboard release debounce expire.
        fresh.key(258); assert fresh.state()[b'buffer']==b'a'
        button=next(b for _,b in fresh.state()[b'buttons'].items() if b[b'name']==b'key' and b[b'value']==b'b')
        fresh.point=(button[b'x']+10,button[b'y']+10); fresh.touch=1; fresh.frame()
        assert fresh.state()[b'buffer']==b'ab'
        fresh.frame(); assert fresh.state()[b'buffer']==b'ab'
        fresh.touch=0; fresh.frame()
        # Staggered duplicate callbacks, key aliases and held keys across slow frames.
        fresh.state()[b'focus']=1
        fresh.held={306,39};fresh.frame();assert fresh.state()[b'focus']==2
        for _ in range(4):fresh.frame()
        fresh.held={39};fresh.frame();assert fresh.state()[b'focus']==2
        fresh.lua.globals()[b'seedsow_editor_key'](fresh.engine,fresh.lua.table_from({b'key':b'306'}))
        fresh.frame();assert fresh.state()[b'focus']==2
        fresh.held=set();fresh.frame();fresh.frame()
        fresh.held={306};fresh.frame();assert fresh.state()[b'focus']==3
        fresh.held=set();fresh.frame();fresh.frame()
        # A script error/instruction loop returns to the editor, not a false success.
        fresh.state()[b'buffer']=b'while true do end'
        fresh.key(256)
        assert fresh.state()[b'running'] is False and b'instruction limit' in fresh.state()[b'status']
        fresh.state()[b'buffer']=b'local n=0; return function(e,api) n=n+1; if n==2 then print("TICK OK"); api.openEditor() end end'
        fresh.key(256); fresh.frame()
        assert fresh.state()[b'running'] is False and fresh.state()[b'output'][1]==b'TICK OK'
        # Keyboard range editing leaves the unedited suffix intact.
        fresh.state()[b'buffer']=b'first\nsecond\nthird'; fresh.state()[b'cursor']=6
        fresh.prompt('line','CHANGED')
        assert fresh.state()[b'buffer']==b'first\nCHANGED\nthird'
        # A damaged user script opens its editable source on restart.
        saved['sscode012.lua']=b'not valid @ lua'
        broken=Console(saved,base/'compile-error',fresh.metadata); broken.load(12)
        assert broken.state()[b'running'] is False
        assert b'could not run' in broken.state()[b'status']
        # Independent per-ASB function names prevent a previously cached slot from
        # borrowing another slot's argument in the same Lua VM.
        broken.load(1); assert broken.state()[b'running'] is not True
        broken.load(4); assert broken.state()[b'running'] is True
        assert b'Hello from a persistent' in broken.state()[b'output'][1]
        bad_ref=dict(files); bad_ref['ssslot004.ref']=b'../outside\n'
        recovery=Console(bad_ref,base/'bad-reference'); recovery.load(1)
        assert recovery.state()[b'running'] is not True
        assert b'could not open' in recovery.state()[b'status']
        recovery.prompt('filename','ssslot004.ref')
        assert recovery.state()[b'buffer']==b'../outside\n'
        # End-to-end controller packet, including repeated held samples per symbol.
        from protocol import pack,symbols
        receiver=Console(files,base/'receiver');receiver.load(2)
        assert receiver.state()[b'receive'] is not None
        packet=pack('pc-proof.lua',b'print("TRANSFER PROOF")\n')
        clock=False
        for nibble in symbols(packet):
            faces={key for bit,key in enumerate((258,257,259,256)) if nibble&(1<<bit)}
            receiver.held=faces|({261} if clock else set());receiver.frame()
            clock=not clock
            receiver.held=faces|({261} if clock else set());receiver.frame();receiver.frame()
        assert receiver.state()[b'filename']==b'pc-proof.lua'
        assert receiver.state()[b'buffer']==b'print("TRANSFER PROOF")\n'
        assert b'PC RECEIVED' in receiver.state()[b'status']
        assert not (receiver.directory/'pc-proof.lua').exists()
        receiver.held=set();receiver.frame();receiver.frame();receiver.action('publish')
        assert (receiver.directory/'pc-proof.lua').read_bytes()==b'print("TRANSFER PROOF")\n'
        # Built-in complex control runs without a Pi, but is labelled as local.
        blue=Console(files,base/'blue-control');blue.load(5)
        assert blue.state()[b'user_fullscreen'] is True
        blue.key(257);assert blue.state()[b'user_fullscreen'] is False
    result={'passed':True,'console_tested':False,'build_id':manifest['build_id'],
        'checks':['archive/hashes, 120 native launch templates',
            'three editor entries, game-menu locks, corrupted-copy repair',
            'native keyboard ASB continuation, source publish and simulated cold restart',
            'all 256 binary byte values, zero-based patching, undo and previous-file recovery',
            'protected editor writes rejected; raw other-slot writes allowed; no traversal',
            'staging/backup failures preserve old target',
            'single input path; staggered aliases, long holds, stale callbacks and releases',
            'user print/frame API, instruction guard and compile-error recovery',
            'line replacement preserves suffix; independent cached-slot boot functions',
            'malformed user reference leaves editor available; game file-allocation metadata populated',
            'checksummed controller upload; no writes before publish; full-screen blue control'],
        'limitations':['This repackaged build still needs its own console trial; original V3 hardware upload/restart passed',
            'Pluto serialization and native commits in this checker are stand-ins; earlier diagnostic proved those APIs on console']}
    (run/'local-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('run',type=Path)
    check(p.parse_args().run.resolve())
