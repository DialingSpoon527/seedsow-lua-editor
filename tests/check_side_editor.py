"""Exercise a side editor through native slot publication, startup and fallback."""
import argparse
import json
import tempfile
import zipfile
from pathlib import Path
from check import Console,expect_error
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'editor'))
from build_side_editor import payload,isolated_source,current_source
from build import load_backup
from check_navigation import check_navigation

ROOT=Path(__file__).resolve().parents[1]
PROFILE=b'A isDown 13\nB isDown 27\nX isDown 113\nY isDown 112\nL isDown 116\nR isDown 117\n'

def publish(c,slot,name,source):
    s=c.state();s[b'slot']=slot;s[b'filename']=name.encode();s[b'buffer']=source;s[b'saved']=b'';s[b'cursor']=0
    c.action('publish')

def disk(c):return {p.name:p.read_bytes() for p in c.directory.iterdir()}

def main(run):
    manifest=json.loads((run/'manifest.json').read_text());program=Path(manifest['lua_file']).read_bytes()
    slot=manifest.get('slot',30)
    program_slot=42 if slot!=42 else 43
    base_zip=Path(manifest['base_save'])
    files=load_backup(base_zip)
    files['ssedit-controls.txt']=PROFILE
    fixed=['saveg.dat']+[f'ssedit{i}.lua' for i in (1,2,3)]+[f'save{i:04d}.dat' for i in (1,2,3)]+[f'sed{i:02d}.asb' for i in (1,2,3)]+[f'ssboot{i}.bin' for i in (1,2,3)]
    with tempfile.TemporaryDirectory() as temporary:
        base=Path(temporary)
        if 'save_zip' in manifest:
            with zipfile.ZipFile(manifest['save_zip']) as archive:
                assert archive.testzip() is None
                packaged={name:archive.read(name) for name in archive.namelist()}
            for name,data in files.items():
                if name!='ssedit-controls.txt':assert packaged[name]==data,name
            ready=Console(packaged,base/'packaged');ready.load(1)
            assert ready.metadata[b'saveslot'][slot][b'file']==f'save{slot:04d}'.encode()
            ready.load(slot);ready.module=ready.lua.globals()[b'seedsow_editor']
            assert ready.state()[b'config'][b'isolated'] is True
            check_navigation(ready)
            cold=Console(disk(ready),base/'packaged-restart',ready.metadata);cold.load(slot)
            cold.module=cold.lua.globals()[b'seedsow_editor']
            assert cold.state()[b'config'][b'isolated'] is True
            cold.load(3);assert not cold.state()[b'config'][b'isolated']
        c=Console(files,base/'publish');c.load(1)
        c.lua.eval(b'function(s) return assert(loadstring(s)) end')(program)
        publish(c,slot,'side-editor30.lua',program)
        c.action('run');c.frame();c.module=c.lua.globals()[b'seedsow_editor']
        assert c.state()[b'config'][b'isolated'] is True
        assert c.state()[b'config'][b'side_slot']==slot
        assert c.state()[b'closed'] is not True
        assert c.state()[b'input'][b'valid'] is True
        assert (c.directory/f'ed{slot:03d}-session.txt').exists()
        check_navigation(c)
        for name in fixed:assert (c.directory/name).read_bytes()==files[name],name
        w=c.module[b'storage']
        for name in fixed:
            assert w[b'put'](b'save:',name.encode(),b'damage')[0] is False,name
        for name in ('ssseed001.bin','ssedit-controls.txt'):
            assert w[b'put'](b'save:',name.encode(),b'damage')[0] is False,name
        assert (c.directory/'ssedit-controls.txt').read_bytes()==PROFILE
        # The running side editor cannot replace its own published slot.
        c.state()[b'slot']=slot
        expect_error(lambda:c.action('publish'),'running side editor')
        # Ordinary user programs remain publishable from the new editor.
        publish(c,program_slot,'from-side.lua',b'print("SIDE PUBLISHED THIS")\n')
        saved=disk(c)
        restart=Console(saved,base/'restart',c.metadata);restart.load(slot);restart.module=restart.lua.globals()[b'seedsow_editor']
        assert restart.state()[b'config'][b'isolated'] is True,(dict(restart.state()[b'config'].items()),restart.state()[b'status'],restart.state()[b'output'])
        assert restart.state()[b'config'][b'side_slot']==slot
        assert restart.state()[b'closed'] is not True
        restart.load(program_slot);assert restart.state()[b'output'][1]==b'SIDE PUBLISHED THIS'
        restart.load(1);assert not restart.state()[b'config'][b'isolated']
        restart.load(3);assert not restart.state()[b'config'][b'isolated']
        # Learn translated physical controls with no preinstalled mapping or Pi.
        uncalibrated=dict(files);uncalibrated.pop('ssedit-controls.txt')
        manual=Console(uncalibrated,base/'manual-calibration');manual.load(1)
        definitions=manual.lua.table()
        for code,label in ((321,b'F5'),(322,b'F6'),(323,b'F1'),(324,b'F2'),(1,b'CLICK')):
            definitions[code]=manual.lua.table_from({b'btn':label})
        manual.lua.globals()[b'csv'][b'advkey'][b'def']=definitions
        publish(manual,slot,'manual-side.lua',program);manual.action('run');manual.frame()
        manual.module=manual.lua.globals()[b'seedsow_editor']
        assert not manual.state()[b'calibrate']
        assert manual.state()[b'input'][b'valid'] is False
        # Both native Switch codes and their standard game/keyboard aliases work
        # immediately, without a learned upload mapping.
        (manual.directory/'standard-keys.lua').write_bytes(b'print("STANDARD BUTTONS WORK")\n')
        manual.state()[b'saved']=manual.state()[b'buffer']
        manual.prompt('filename','standard-keys.lua')
        for _ in range(4):manual.frame()
        for left,right,x,y in ((260,261,259,256),(116,117,112,113),(321,322,323,324)):
            manual.key(right);assert manual.state()[b'cursor']==1
            assert b'p[|]rint' in manual.messages[b'zzzzsseditor.p1']
            manual.key(left);assert manual.state()[b'cursor']==0
            manual.key(x);assert manual.modal is not None
            manual.reply('')
            for _ in range(4):manual.frame()
            manual.key(y);assert manual.state()[b'running'] is True
            assert manual.state()[b'output'][1]==b'STANDARD BUTTONS WORK'
            manual.key(257);assert manual.state()[b'running'] is False
        assert manual.state()[b'input'][b'valid'] is False
        assert not (manual.directory/f'ed{slot:03d}-controls.txt').exists()
        # Mouse/touch must not also be treated as controller A and insert twice.
        for _ in range(4):manual.frame()
        before=manual.state()[b'buffer']
        button=next(b for _,b in manual.state()[b'buttons'].items() if b[b'name']==b'key' and b[b'value']==b'a')
        manual.point=(button[b'x']+10,button[b'y']+10);manual.touch=1;manual.frame();manual.frame()
        assert manual.state()[b'buffer']==b'a'+before
        manual.touch=0;manual.point=(-1,-1);manual.frame()
        manual.action('undo');manual.frame();assert manual.state()[b'buffer']==before
        # Explicit calibration still supports a nonstandard or Pi input mapping.
        manual.action('calibrate');assert manual.state()[b'calibrate'] is True
        for _ in range(5):manual.frame()
        physical={'A':13,'B':27,'X':113,'Y':112,'L':116,'R':117}
        for button in ('A','B','X','Y','L','R'):
            manual.held={physical[button]}
            for _ in range(6):manual.frame()
            manual.held=set()
            for _ in range(6):manual.frame()
        assert manual.state()[b'calibrate'] is False
        assert manual.state()[b'receive'] is None
        assert manual.state()[b'input'][b'valid'] is True
        assert (manual.directory/f'ed{slot:03d}-controls.txt').exists()
        assert not (manual.directory/'ssedit-controls.txt').exists()
        (manual.directory/'manual-keys.lua').write_bytes(b'print("PHYSICAL BUTTONS WORK")\n')
        manual.state()[b'saved']=manual.state()[b'buffer']
        manual.prompt('filename','manual-keys.lua')
        for _ in range(4):manual.frame()
        assert manual.layers[b'zzzzsseditor.p1'][b'height']==28
        assert manual.layers[b'zzzzsseditor.p1'][b'size']==20
        manual.key(physical['R']);assert manual.state()[b'cursor']==1
        assert b'p[|]rint' in manual.messages[b'zzzzsseditor.p1']
        manual.key(physical['L']);assert manual.state()[b'cursor']==0
        manual.key(physical['X']);assert manual.modal is not None
        manual.reply('')
        for _ in range(4):manual.frame()
        manual.key(physical['Y']);assert manual.state()[b'running'] is True
        assert manual.state()[b'output'][1]==b'PHYSICAL BUTTONS WORK'
        manual.key(physical['B']);assert manual.state()[b'running'] is False
        recalibrated=Console(disk(manual),base/'manual-restart',manual.metadata)
        recalibrated.load(slot);recalibrated.module=recalibrated.lua.globals()[b'seedsow_editor']
        assert recalibrated.state()[b'input'][b'valid'] is True
        assert not recalibrated.state()[b'calibrate']
        for name in fixed:assert (manual.directory/name).read_bytes()==files[name],name
        # Corrupt reconstruction is rejected before candidate code is executed.
        crc=str(manifest['source_adler32']).encode();assert program.count(crc)==1
        damaged=program.replace(crc,str(manifest['source_adler32']+1).encode())
        bad=Console(files,base/'bad-checksum');bad.load(1)
        publish(bad,slot,'bad-side.lua',damaged);bad.action('run');bad.frame();bad.module=bad.lua.globals()[b'seedsow_editor']
        assert not bad.state()[b'config'][b'isolated']
        assert bad.state()[b'running'] is False
        assert b'reconstruction failed' in bad.state()[b'status']
        for name in fixed:assert (bad.directory/name).read_bytes()==files[name]
        # A validly compiled candidate that raises during startup restores the
        # prior callbacks/editor, without recursively rerunning the failed slot.
        core=isolated_source(current_source(),slot)
        before=b'function Editor.start(engine,config,source)\n'
        core=core.replace(before,before+b'    error("SIMULATED START FAILURE")\n',1)
        failure=payload(files['ssedit1.lua'],core,slot,'startup-failure-test')
        failed=Console(files,base/'start-failure');failed.load(1)
        publish(failed,slot,'failed-side.lua',failure);failed.action('run');failed.frame();failed.module=failed.lua.globals()[b'seedsow_editor']
        assert not failed.state()[b'config'][b'isolated']
        assert failed.state()[b'closed'] is not True
        assert failed.state()[b'running'] is False
        assert b'SIMULATED START FAILURE' in failed.state()[b'status']
        for name in fixed:assert (failed.directory/name).read_bytes()==files[name]
        failed.load(3);assert not failed.state()[b'config'][b'isolated']
    result={'passed':True,'hardware_tested':False,'checks':[
        'normal save publication launches the updated editor from a user slot',
        'line movement preserves column; independent line/page scrolling and cursor visibility survive edits',
        'measured touch placement handles proportional text, tabs, escaped bytes and scrolled offsets',
        'code window focus, D-pad cursor mode, held arrows and B exit preserve the buffer',
        'left-edge indicator is light on hover/focus and black while selected',
        'standard Switch and game input aliases work without calibration; optional learned mappings persist',
        'source delta reconstructs and validates the entire candidate before execution',
        'candidate sessions are separate; original input calibration is only read',
        'original core, three recovery entries, launch assets and calibration stay byte-identical',
        'candidate storage API rejects direct writes to original recovery files',
        'candidate reserves its own slot while still publishing other user programs',
        'side editor and a program it publishes load after simulated cold restart',
        'damaged reconstruction stays in the original editor',
        'runtime startup failure restores previous callbacks/editor; recovery slot still loads'],
        'limits':['depends on retained loader/core','unrestricted user Lua can bypass storage policy','not an atomic self-updater']}
    (run/'local-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);main(p.parse_args().run)
