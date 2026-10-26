"""Validate the original public starter, its privacy boundary and actual Lua.

Separate from general compatible-save tests: --base must be a reviewed starter
or an editor installation with the exact reviewed native starter state.
"""
import argparse
import hashlib
import json
import sys
import tempfile
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT/'tests'), str(ROOT/'tools')]
from package_save import package_save, starter_files, STARTER_HASHES
from indexed_save import IndexedSave, Edit, string


def write_zip(path, files):
    with zipfile.ZipFile(path, 'w') as archive:
        for name, data in files.items():
            archive.writestr(name, data)


def main(base):
    from check import check
    from check_v3 import main as check_v3
    before = hashlib.sha256(base.read_bytes()).digest()
    with tempfile.TemporaryDirectory() as temp:
        work = Path(temp)
        # Inject private files to exercise the publication exclusion boundary.
        from build import load_backup
        files = load_backup(base)
        private = {'custom.lua': b'PRIVATE', 'ssedit-input-report.txt': b'PRIVATE',
                   'sscode020.lua': b'PRIVATE', 'seedsow-connection.json': b'PRIVATE'}
        files.update(private)
        private_zip = work/'private.zip'
        write_zip(private_zip, files)
        starter = work/'starter'
        public = package_save(private_zip, starter)
        with zipfile.ZipFile(public['zip']) as archive:
            assert not set(private) & set(archive.namelist())
            meta = archive.read('.nx_save_meta.bin')
            assert len(meta) == 86 and meta[13:29] == bytes(16)
            assert meta[49:57] == bytes(8) and meta[77:85] == bytes(8)
            files = {n: archive.read(n) for n in archive.namelist()}
        (starter/'manifest.json').write_text(json.dumps({
            'build_id': 'public-starter', 'version': 3, 'entry_label': 'LUA EDITOR V3',
            'source_sha256': {}, 'save_files': {n: hashlib.sha256(b).hexdigest()
                                             for n, b in files.items()}}))
        check(starter)
        check_v3(starter)
        # Equivalent zlib encodings remain accepted; all decoded structure matters.
        variant = dict(files)
        native = variant['ssseed020.bin']
        variant['ssseed020.bin'] = native[:12]+zlib.compress(IndexedSave(native).body, 1)
        variant_zip = work/'different-compression.zip'
        write_zip(variant_zip, variant)
        package_save(variant_zip, work/'portable-compression')
        # Exercise every native hash guard and a structurally changed launcher.
        for name in (*STARTER_HASHES, 'ssseed020.bin'):
            altered = dict(files)
            altered[name] += b'TAMPER'
            bad = work/'altered.zip'
            write_zip(bad, altered)
            try:
                starter_files(bad)
            except (ValueError, KeyError, AssertionError, zlib.error):
                pass
            else:
                raise AssertionError('Altered starter accepted: '+name)
        # Validly encoded native data with the wrong target must also fail.
        altered = dict(files)
        seed = IndexedSave(files['ssseed020.bin'])
        caret = seed.groups[seed.groups[0][3]]
        altered['ssseed020.bin'] = seed.apply([
            Edit(caret[3], string('save:/ss020.asb'), string('save:/ss021.asb'))])
        bad = work/'wrong-launcher.zip'
        write_zip(bad, altered)
        try:
            starter_files(bad)
        except ValueError:
            pass
        else:
            raise AssertionError('Structurally altered launcher accepted.')
    assert hashlib.sha256(base.read_bytes()).digest() == before
    print('Reviewed starter privacy, hashes, structure, portable compression and Lua checks passed. Input unchanged.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    main(parser.parse_args().base.resolve())
