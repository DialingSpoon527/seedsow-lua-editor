"""Create a source-only ZIP from an explicit public-file allowlist."""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_FILES = (
    '.github/workflows/release.yml',
    '.gitattributes', '.gitignore', 'README.md', 'LICENSE', 'VERSION', 'CHANGELOG.md',
    'THIRD_PARTY_NOTICES.md', 'START WINDOWS.cmd', 'requirements-dev.txt',
    'docs/01-console-install.md', 'docs/02-pi-setup.md', 'docs/03-send-files.md',
    'docs/04-updates-recovery.md', 'docs/05-troubleshooting.md', 'docs/06-development.md',
    'docs/07-console-editor.md',
    'docs/compatibility.md', 'tools/README.md', 'tools/jksv_metadata.py',
    'docs/images/console-editor.jpg', 'docs/images/save-menu.jpg', 'docs/images/included-example.jpg',
    'editor/build.py', 'editor/build_side_editor.py', 'editor/editor.lua',
    'editor/input.lua', 'editor/storage.lua', 'editor/transfer.lua',
    'examples/hello.lua', 'examples/blue.lua', 'licenses/NXBT-MIT.txt',
    'pc/app.py', 'pc/client.py', 'pc/protocol.py',
    'pi/pi_bridge.py', 'pi/pairing_agent.py', 'pi/patch_nxbt.py', 'pi/install.sh',
    'pi/export_connection.py', 'pi/seedsow-input.service',
    'tests/check.py', 'tests/check_v3.py', 'tests/check_side_editor.py',
    'tests/test_pc.py', 'tests/run_checks.py', 'tests/smoke_gui.py',
    'tests/test_release.py', 'tests/test_layout.py', 'tests/test_metadata.py',
    'tools/asb.py', 'tools/indexed_save.py', 'tools/save_globals.py',
    'maintainer/README.md', 'maintainer/RELEASE_NOTES.md',
    'maintainer/package_release.py', 'maintainer/publish_release.py',
    'maintainer/package_save.py', 'maintainer/check_starter.py',
)


def source_files():
    files = {}
    for name in PUBLIC_FILES:
        path = ROOT/name
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT) or not path.is_file():
            raise ValueError('Missing or linked public source file: '+name)
        data = path.read_bytes()
        if path.suffix.lower() not in ('.jpg','.jpeg','.png','.gif','.webp'):
            data = data.replace(b'\r\n', b'\n')
            if name.endswith('.cmd'):
                data = data.replace(b'\n',b'\r\n')
        if re.search(rb'-----BEGIN [A-Z ]*PRIVATE KEY-----',data):
            raise ValueError('Private key material in '+name)
        files[name] = data
    return files


def package(output=None):
    version = (ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+',version):
        raise ValueError('Invalid release version.')
    files = source_files()
    out = Path(output) if output else ROOT/'dist'
    out.mkdir(parents=True,exist_ok=True)
    target = out/f'seedsow-lua-editor-{version}.zip'
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,data in sorted(files.items()):
            info = zipfile.ZipInfo('seedsow-lua-editor/'+name,date_time=(2026,1,1,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100755 if name.endswith('.sh') else 0o100644)<<16
            archive.writestr(info,data)
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None or len(archive.infolist()) != len(files):
            raise ValueError('Release archive verification failed.')
        for name,data in files.items():
            if archive.read('seedsow-lua-editor/'+name) != data:
                raise ValueError('Release member differs: '+name)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix('.zip.sha256').write_text(digest+'  '+target.name+'\n',encoding='ascii')
    manifest = {'version':version, 'archive':target.name, 'sha256':digest,
                'files':{n:hashlib.sha256(b).hexdigest() for n,b in sorted(files.items())}}
    target.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return {'zip':str(target.resolve()),'sha256':digest,'files':len(files),'bytes':target.stat().st_size}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path)
    print(json.dumps(package(p.parse_args().output),indent=2))
