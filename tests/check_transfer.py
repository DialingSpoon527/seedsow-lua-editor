"""Transfer regressions: learn actual aliases, latch errors, and persist PC files."""
import argparse
import json
import math
import sys
import tempfile
import threading
import time
import zipfile
from pathlib import Path
from urllib.request import Request,urlopen
from check import Console

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'pc'),str(ROOT/'pi')]
from protocol import pack,symbols,BUTTONS
from pi_bridge import Bridge,make_server

def settle(c,frames=4):
    c.held=set()
    for _ in range(frames):c.frame()

def send(c,packet,keys):
    clock=False;settle(c)
    for nibble in symbols(packet):
        faces={keys[b] for bit,b in enumerate(BUTTONS) if nibble&(1<<bit)}
        c.held=faces|({keys['R']} if clock else set());c.frame()
        clock=not clock;c.held=faces|({keys['R']} if clock else set());c.frame();c.frame()
    settle(c)

def main(run):
    with zipfile.ZipFile(run/'Seedsow-Lua-Editor-Save.zip') as z:files={n:z.read(n) for n in z.namelist()}
    # This intentionally differs from V2's assumptions and reverses X/Y codes.
    keys={'A':13,'B':27,'X':113,'Y':112,'L':116,'R':117}
    with tempfile.TemporaryDirectory() as temp:
        base=Path(temp);c=Console(files,base/'calibrate');c.load(2)
        assert c.state()[b'calibrate'] is True
        settle(c)
        for button in ('A','B','X','Y','L','R'):
            c.held={keys[button]}
            for _ in range(6):c.frame()
            settle(c,6)
        assert c.state()[b'calibrate'] is False
        assert c.state()[b'receive'] is not None
        assert c.state()[b'input'][b'valid'] is True
        assert (c.directory/'ssedit-controls.txt').exists()
        for b,k in keys.items():assert c.state()[b'input'][b'map'][b.encode()][b'codes'][1]==k
        # Real HTTP calibration request drives the generated Pi macro into a
        # fresh console stand-in using physical button names and native aliases.
        api=Console(files,base/'http-calibration');api.load(2)
        class FakeNX:
            def __init__(self):self.state={0:{'state':'connected','errors':False,'finished_macros':[]}}
            def macro(self,index,program,block=False):
                for line in program.splitlines():
                    parts=line.split();api.held={keys[b] for b in parts[:-1]}
                    for _ in range(max(1,math.ceil(float(parts[-1][:-1])/.2))):api.frame()
                self.state[0]['finished_macros'].append('calibration-test');return 'calibration-test'
        bridge=Bridge(FakeNX(),None);bridge.controller=0
        server=make_server(bridge,'local-calibration-test','127.0.0.1',0)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            request=Request('http://127.0.0.1:'+str(server.server_port)+'/calibrate',data=b'{}',headers={'Authorization':'Bearer local-calibration-test','Content-Type':'application/json'})
            with urlopen(request,timeout=5) as response:json.load(response)
            deadline=time.monotonic()+5
            while bridge.transfer and time.monotonic()<deadline:time.sleep(.01)
            assert bridge.last['state']=='calibration inputs sent',bridge.last
            assert api.state()[b'input'][b'valid'] and api.state()[b'receive'] is not None
        finally:server.shutdown();server.server_close();thread.join()
        # A malformed header latches. Subsequent A/B/X/Y never enter menu actions.
        wrong=b'bad!'+pack('x.lua',b'abc')[4:]
        send(c,wrong,keys)
        assert c.state()[b'receive'][b'error']
        assert b'Expected 53 53 45 32 01' in c.state()[b'status']
        assert (c.directory/'ssedit-transfer-report.txt').exists()
        original=c.state()[b'buffer']
        for k in (keys['A'],keys['B'],keys['X'],keys['Y']):c.key(k)
        assert c.state()[b'receive'][b'error'] and c.state()[b'buffer']==original
        # A slow next frame must not turn trailing receive buttons into UI input.
        c.held={keys['L'],keys['Y']};c.frame()
        assert c.state()[b'receive'] is None
        c.clock+=1000;c.frame()
        assert not c.state()[b'running']
        settle(c)
        c.action('receive');assert c.state()[b'receive'][b'count']==0
        payload=b'print("WINDOWS FILE CHECK")\n'
        send(c,pack('P020_pc-proof.lua',payload),keys)
        assert c.state()[b'receive'][b'complete'] is True
        assert c.state()[b'slot']==20 and c.state()[b'filename']==b'pc-proof.lua'
        assert (c.directory/'pc-proof.lua').read_bytes()==payload
        assert (c.directory/'save0020.dat').read_bytes()==files['ssseed020.bin']
        assert b'PC FILE SAVED' in c.state()[b'status']
        # Completion is latched too, so trailing sender inputs cannot edit source.
        c.key(keys['A']);assert c.state()[b'buffer']==payload
        c.key(keys['L']);assert c.state()[b'receive'] is None
        disk={p.name:p.read_bytes() for p in c.directory.iterdir()}
        reboot=Console(disk,base/'restart',c.metadata);reboot.load(20)
        assert reboot.state()[b'output'][1]==b'WINDOWS FILE CHECK'
        assert reboot.state()[b'input'][b'valid'] is True
        reboot.load(2);assert not reboot.state()[b'calibrate'] and reboot.state()[b'receive']
        raw=bytes(range(256));send(reboot,pack('F000_binary.dat',raw),keys)
        assert (reboot.directory/'binary.dat').read_bytes()==raw
        for name in ('save0001.dat','save0002.dat','save0003.dat','ssedit1.lua','ssedit2.lua','ssedit3.lua'):
            assert (reboot.directory/name).read_bytes()==files[name]
        reboot.key(keys['L']);reboot.action('receive')
        corrupt=bytearray(pack('F000_never.dat',b'checksum test'));corrupt[-1]^=1
        send(reboot,bytes(corrupt),keys)
        assert not (reboot.directory/'never.dat').exists()
        assert b'Checksum mismatch' in reboot.state()[b'status']
        reboot.key(keys['L']);reboot.action('receive')
        send(reboot,pack('P001_bad.lua',b'print(1)'),keys)
        assert b'Protected or invalid' in reboot.state()[b'status']
        assert not (reboot.directory/'bad.lua').exists()
        reboot.key(keys['L']);reboot.action('receive');send(reboot,b'SSE2\x01',keys)
        for _ in range(55):reboot.frame()
        assert b'Incomplete packet' in reboot.state()[b'status']
    result={'passed':True,'hardware_transfer_confirmed':False,'checks':[
        'calibration learns translated key IDs and reversed X/Y from held samples',
        'real HTTP calibration request drives the Pi macro and learns the same profile',
        'invalid header is visible, reported, and latched against all trailing face presses',
        'L cancels and a new Receive starts at zero without a second unsaved-buffer prompt',
        'controller upload saves source and publishes chosen slot; simulated restart runs it',
        'calibration survives restart; slot 2 directly arms future uploads',
        'raw data preserves all 256 bytes; checksum failures and editor-slot destinations reject',
        'partial input times out visibly and remains latched',
        'three editor entries and recovery sources remain unchanged']}
    (run/'transfer-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);main(p.parse_args().run)
