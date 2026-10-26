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
from build import build, core_source, load_backup
from build_side_editor import payload, isolated_source
from check import check
from check_v3 import main as check_v3
from check_side_editor import main as check_side
from package_save import package_save


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
        # The public starter excludes personal files and account metadata, and
        # its exact packaged bytes still run through the editor/upload checks.
        starter = Path(temp)/'starter'
        public = package_save(archive,starter)
        with zipfile.ZipFile(public['zip']) as z:
            assert not {'custom.lua','ssedit-input-report.txt','sscode020.lua'} & set(z.namelist())
            meta = z.read('.nx_save_meta.bin')
            assert len(meta)==86 and meta[13:29]==bytes(16) and meta[49:57]==bytes(8) and meta[77:85]==bytes(8)
            files = {n:z.read(n) for n in z.namelist()}
        (starter/'manifest.json').write_text(json.dumps({
            'build_id':'public-starter','version':3,'entry_label':'LUA EDITOR V3','source_sha256':{},
            'save_files':{n:hashlib.sha256(b).hexdigest() for n,b in files.items()}}))
        check(starter)
        check_v3(starter)
        # A different compression encoding of the same native fields is portable.
        import zlib
        from indexed_save import IndexedSave
        variant = dict(files)
        native = variant['ssseed020.bin']
        variant['ssseed020.bin'] = native[:12]+zlib.compress(IndexedSave(native).body,1)
        variant_zip = Path(temp)/'different-compression.zip'
        with zipfile.ZipFile(variant_zip,'w') as z:
            for name,data in variant.items():z.writestr(name,data)
        package_save(variant_zip,Path(temp)/'portable-compression')
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
    print('Editor, prebuilt-save privacy, upload, rebuild preservation and update recovery checks passed. Input backup unchanged.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',type=Path,required=True)
    main(p.parse_args().base.resolve())
