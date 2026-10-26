"""Exercise a side editor through real V3 publication, startup and fallback."""
import argparse
import json
import tempfile
import zipfile
import zlib
from pathlib import Path
from check import Console,expect_error
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'editor'))
from build_side_editor import payload,isolated_source

ROOT=Path(__file__).resolve().parents[1]
BASE=None
PROFILE=b'A isDown 13\nB isDown 27\nX isDown 113\nY isDown 112\nL isDown 116\nR isDown 117\n'

def publish(c,slot,name,source):
    s=c.state();s[b'slot']=slot;s[b'filename']=name.encode();s[b'buffer']=source;s[b'saved']=b'';s[b'cursor']=0
    c.action('publish')

def disk(c):return {p.name:p.read_bytes() for p in c.directory.iterdir()}

def main(run):
    manifest=json.loads((run/'manifest.json').read_text());program=Path(manifest['lua_file']).read_bytes()
    base_zip=Path(manifest['base_save'])
    with zipfile.ZipFile(base_zip) as z:files={n:z.read(n) for n in z.namelist()}
    files['ssedit-controls.txt']=PROFILE
    fixed=['saveg.dat']+[f'ssedit{i}.lua' for i in (1,2,3)]+[f'save{i:04d}.dat' for i in (1,2,3)]+[f'sed{i:02d}.asb' for i in (1,2,3)]+[f'ssboot{i}.bin' for i in (1,2,3)]
    with tempfile.TemporaryDirectory() as temporary:
        base=Path(temporary);c=Console(files,base/'publish');c.load(1)
        c.lua.eval(b'function(s) return assert(loadstring(s)) end')(program)
        publish(c,30,'side-editor30.lua',program)
        c.action('run');c.frame();c.module=c.lua.globals()[b'seedsow_editor']
        assert c.state()[b'config'][b'isolated'] is True
        assert c.state()[b'config'][b'side_slot']==30
        assert c.state()[b'closed'] is not True
        assert c.state()[b'input'][b'valid'] is True
        assert (c.directory/'ed030-session.txt').exists()
        for name in fixed:assert (c.directory/name).read_bytes()==files[name],name
        w=c.module[b'storage']
        for name in fixed:
            assert w[b'put'](b'save:',name.encode(),b'damage')[0] is False,name
        for name in ('ssseed001.bin','ssedit-controls.txt'):
            assert w[b'put'](b'save:',name.encode(),b'damage')[0] is False,name
        assert (c.directory/'ssedit-controls.txt').read_bytes()==PROFILE
        # The running side editor cannot replace its own published slot.
        c.state()[b'slot']=30
        expect_error(lambda:c.action('publish'),'running side editor')
        # Ordinary user programs remain publishable from the new editor.
        publish(c,42,'from-side.lua',b'print("SIDE PUBLISHED THIS")\n')
        saved=disk(c)
        restart=Console(saved,base/'restart',c.metadata);restart.load(30);restart.module=restart.lua.globals()[b'seedsow_editor']
        assert restart.state()[b'config'][b'isolated'] is True,(dict(restart.state()[b'config'].items()),restart.state()[b'status'],restart.state()[b'output'])
        assert restart.state()[b'config'][b'side_slot']==30
        assert restart.state()[b'closed'] is not True
        restart.load(42);assert restart.state()[b'output'][1]==b'SIDE PUBLISHED THIS'
        restart.load(1);assert not restart.state()[b'config'][b'isolated']
        restart.load(3);assert not restart.state()[b'config'][b'isolated']
        # Corrupt reconstruction is rejected before candidate code is executed.
        crc=str(manifest['source_adler32']).encode();assert program.count(crc)==1
        damaged=program.replace(crc,str(manifest['source_adler32']+1).encode())
        bad=Console(files,base/'bad-checksum');bad.load(1)
        publish(bad,30,'bad-side.lua',damaged);bad.action('run');bad.frame();bad.module=bad.lua.globals()[b'seedsow_editor']
        assert not bad.state()[b'config'][b'isolated']
        assert bad.state()[b'running'] is False
        assert b'reconstruction failed' in bad.state()[b'status']
        for name in fixed:assert (bad.directory/name).read_bytes()==files[name]
        # A validly compiled candidate that raises during startup restores the
        # prior callbacks/editor, without recursively rerunning the failed slot.
        core=isolated_source(files['ssedit1.lua'],30)
        before=b'function Editor.start(engine,config,source)\n'
        core=core.replace(before,before+b'    error("SIMULATED START FAILURE")\n',1)
        failure=payload(files['ssedit1.lua'],core,30,'startup-failure-test')
        failed=Console(files,base/'start-failure');failed.load(1)
        publish(failed,30,'failed-side.lua',failure);failed.action('run');failed.frame();failed.module=failed.lua.globals()[b'seedsow_editor']
        assert not failed.state()[b'config'][b'isolated']
        assert failed.state()[b'closed'] is not True
        assert failed.state()[b'running'] is False
        assert b'SIMULATED START FAILURE' in failed.state()[b'status']
        for name in fixed:assert (failed.directory/name).read_bytes()==files[name]
        failed.load(3);assert not failed.state()[b'config'][b'isolated']
    result={'passed':True,'hardware_tested':False,'checks':[
        'normal V3 save publication launches the updated editor from a user slot',
        'source delta reconstructs and validates the entire candidate before execution',
        'candidate sessions are separate; original input calibration is only read',
        'original core, three recovery entries, launch assets and calibration stay byte-identical',
        'candidate storage API rejects direct writes to original recovery files',
        'candidate reserves its own slot while still publishing other user programs',
        'side editor and a program it publishes load after simulated cold restart',
        'damaged reconstruction stays in the original editor',
        'runtime startup failure restores previous callbacks/editor; recovery slot still loads'],
        'limits':['depends on retained V3 loader/core','unrestricted user Lua can bypass storage policy','not an atomic self-updater']}
    (run/'local-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);main(p.parse_args().run)
