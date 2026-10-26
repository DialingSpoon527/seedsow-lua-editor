"""Run editor regressions using a private compatible backup supplied by the caller."""
import argparse
import hashlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'editor'))
sys.path.insert(0,str(ROOT/'tools'))
from build import build, core_source
from build_side_editor import payload, isolated_source
from check import check
from check_v3 import main as check_v3
from check_side_editor import main as check_side


def main(base):
    before = hashlib.sha256(base.read_bytes()).digest()
    with tempfile.TemporaryDirectory() as temp:
        run = Path(temp)/'base'
        build(base,run,replace_slots=True)
        check(run)
        check_v3(run)
        # Keep custom programs and unrelated save files through a rebuild.
        archive = run/'Seedsow-Lua-Editor-Save.zip'
        with zipfile.ZipFile(archive,'a') as z:
            z.writestr('custom.lua',b'print("KEEP ME")\n')
            z.writestr('ssedit-input-report.txt',b'TEST PRIVATE REPORT')
            z.writestr('sscode020.lua',b'print("TEST PRIVATE PROGRAM")')
        import zlib
        rebuilt = Path(temp)/'rebuilt'
        build(archive,rebuilt)
        with zipfile.ZipFile(rebuilt/'Seedsow-Lua-Editor-Save.zip') as z:
            assert z.read('custom.lua')==b'print("KEEP ME")\n'
        side = Path(temp)/'side'
        side.mkdir()
        source = core_source()
        updated = isolated_source(source,30)
        program = payload(source,updated,30,'local-check')
        target = side/'Side-Editor-V3B-slot-30.lua'
        target.write_bytes(program)
        (side/'manifest.json').write_text(json.dumps({'lua_file':str(target),'base_save':str(archive),
                                                      'source_adler32':zlib.adler32(updated)}))
        check_side(side)
    assert hashlib.sha256(base.read_bytes()).digest()==before
    print('Editor, upload, rebuild preservation and update recovery checks passed. Input backup unchanged.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',type=Path,required=True)
    main(p.parse_args().base.resolve())
