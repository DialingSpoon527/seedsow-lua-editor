"""Run editor regressions using a private compatible backup supplied by the caller."""
import argparse
import hashlib
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'editor'))
sys.path.insert(0,str(ROOT/'tools'))
from build import build
from build_side_editor import build_update
from check import check
from check_transfer import main as check_transfer
from check_side_editor import main as check_side
from check import Console
from check_navigation import check_navigation


def main(base):
    before = hashlib.sha256(base.read_bytes()).digest()
    with tempfile.TemporaryDirectory() as temp:
        run = Path(temp)/'base'
        build(base,run,replace_slots=True,legacy=True)
        check(run)
        check_transfer(run)
        # Keep custom programs and unrelated save files through a rebuild.
        archive = run/'Seedsow-Lua-Editor-Save.zip'
        with zipfile.ZipFile(archive,'a') as z:
            z.writestr('custom.lua',b'print("KEEP ME")\n')
            z.writestr('ssedit-input-report.txt',b'TEST PRIVATE REPORT')
            z.writestr('sscode020.lua',b'print("TEST PRIVATE PROGRAM")')
        rebuilt = Path(temp)/'rebuilt'
        build(archive,rebuilt,legacy=True)
        with zipfile.ZipFile(rebuilt/'Seedsow-Lua-Editor-Save.zip') as z:
            assert z.read('custom.lua')==b'print("KEEP ME")\n'
        side = Path(temp)/'side'
        info = build_update(archive,30,side,include_save=True)
        check_side(side)
        # Packaging must never silently replace a user program or a previous build.
        for backup,out in ((Path(info['save_zip']),Path(temp)/'occupied'), (archive,side)):
            try:
                build_update(backup,30,out,include_save=True)
            except ValueError:
                pass
            else:
                raise AssertionError('Expected occupied slot/output rejection')
        # The same backup in a single enclosing JKSV directory is supported.
        nested = Path(temp)/'nested.zip'
        with zipfile.ZipFile(archive) as old, zipfile.ZipFile(nested,'w') as new:
            for name in old.namelist():
                new.writestr('backup/'+name,old.read(name))
        build_update(nested,31,Path(temp)/'nested-update',include_save=True)
        check_side(Path(temp)/'nested-update')
        current=Path(temp)/'current'
        build(base,current,replace_slots=True)
        check(current)
        check_transfer(current)
        with zipfile.ZipFile(current/'Seedsow-Lua-Editor-Save.zip') as z:
            current_files={n:z.read(n) for n in z.namelist()}
        c=Console(current_files,Path(temp)/'main-editor');c.load(1)
        assert c.messages[b'zzzzsseditor.title']==b'SEEDSOW LUA EDITOR'
        assert not c.state()[b'config'][b'isolated']
        check_navigation(c)
        check_side_path=Path(temp)/'current-side'
        build_update(current/'Seedsow-Lua-Editor-Save.zip',30,check_side_path,include_save=True)
        check_side(check_side_path)
    assert hashlib.sha256(base.read_bytes()).digest()==before
    print('Editor, upload, rebuild preservation and update recovery checks passed. Input backup unchanged.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',type=Path,required=True)
    main(p.parse_args().base.resolve())
