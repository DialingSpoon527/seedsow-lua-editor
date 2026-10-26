"""Package a reviewed starter save for users who only want to restore it.

Only the known starter state and editor assets are accepted. Personal account
metadata, calibration, reports, sessions, arbitrary files and user programs are
excluded. The public output can itself be used as this tool's input.
"""
import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'editor'))
from build import core_source, bootstrap, load_backup
from indexed_save import IndexedSave, Edit, string
from asb import decode_asb
from jksv_metadata import portable_account_metadata

STARTER_TITLE_ID = 0x010042D022AEA000

STARTER_HASHES = {
    'saveg.dat':'c06dad53e67daa2a7c7c3758c80aee623e65c4cc16c74551cd8478f8a519235f',
    'system.dat':'dbcae45f01eabfc319a1e4ae74b79f8b75e3f88ff191f503251084c8cf6156de',
    'autosave.dat':'c2810a442ed0fd7cc606a674f83be275915bff778ad3db8c157a0d42ae5ec057',
    'save0121.dat':'3f1004df09a04d9df148dc43ce5b40f5eb21b5cd44b691a56bcee069af4bf6a4',
    'save0001.dat':'7a6d80fe074425d950a544a0746ab8e6d9310113471ee4a3f561dd1a908f0290',
    'save0002.dat':'fa1ffcb1b2e271f1198fc0be68c3f0e14dbf93a7443519d7ced2ff3c17ba5762',
    'save0003.dat':'a903a1f6636e2f33caa435c5859456e4139a8f90e18e5af912a0aa549e4d481f',
    'save0004.dat':'15ac80a26728912c91ad1220e874c55cf43d2c88a4a3a2c33f4911a6e8d507d4',
    'save0005.dat':'db1084ea73109273f365269cb9f0affd722fbf6e8176b82373b4f5bd2c201a6b',
}


def portable_metadata():
    """JKSV revision 1: public game attributes with no personal identifiers.

    Layout: https://github.com/J-D-K/JKSV/blob/rewrite/include/fs/SaveMetaData.hpp
    Existing-save restore uses the target save and recorded data/journal sizes:
    https://github.com/J-D-K/JKSV/blob/rewrite/source/fs/SaveMetaData.cpp
    """
    return portable_account_metadata(STARTER_TITLE_ID, owner_id=STARTER_TITLE_ID,
                                     data_size=32*1024*1024, journal_size=32*1024*1024)


def starter_files(base):
    files = load_backup(base)
    for name,expected in STARTER_HASHES.items():
        if name not in files or hashlib.sha256(files[name]).hexdigest()!=expected:
            raise ValueError('Not the reviewed starter state: '+name+'. Personal backups cannot be published by this tool.')
    core = core_source()
    if any(files.get(f'ssedit{i}.lua')!=core for i in (1,2,3)):
        raise ValueError('The starter editor core must match the release source.')
    template = IndexedSave(files['save0001.dat'])
    caret = template.groups[template.groups[0][3]]
    result = {name:files[name] for name in STARTER_HASHES}
    for slot in range(1,121):
        script = f'sed{slot:02d}.asb' if slot<=3 else f'ss{slot:03d}.asb'
        seed = template.apply([Edit(caret[3],string('save:/sed01.asb'),string('save:/'+script))])
        name = f'ssseed{slot:03d}.bin'
        if name not in files:
            raise ValueError('Missing native launcher template for slot '+str(slot))
        actual,expected = IndexedSave(files[name]),IndexedSave(seed)
        # Different zlib versions may encode the same native save differently.
        # Compare its complete decoded contents and index, retaining reviewed bytes.
        if actual.fields!=expected.fields or actual.groups!=expected.groups:
            raise ValueError('Unexpected native launcher template for slot '+str(slot))
        launch = files.get(script,b'')
        commands = decode_asb(launch)
        text = commands[0][2].get('script','')
        match = re.search(r'build_id="([0-9a-f]{8})"',text)
        if not match:
            raise ValueError('Missing launcher build identifier.')
        import zlib
        if launch!=bootstrap(slot,zlib.adler32(core),match[1]):
            raise ValueError('Unexpected launcher code in '+script)
        result[name] = files[name]
        result[script] = launch
        if slot<=3:
            result[f'ssboot{slot}.bin'] = launch
            result[f'ssedit{slot}.lua'] = core
    # Use the reviewed, generic game-scene thumbnail for every starter entry.
    thumb = files['save0001.png']
    if hashlib.sha256(thumb).hexdigest()!='2f4e2ede1bcd93848291154a6bb2d2bd048098345167ec71954006612b64b331':
        raise ValueError('Unrecognized starter thumbnail.')
    for slot in (1,2,3,4,5,121):
        for suffix in ('.png','_s.png'):
            result[f'save{slot:04d}{suffix}'] = thumb
    result['ssethumb.png'] = thumb
    result['sscode004.lua'] = b'print("Hello from a persistent Lua slot!")\nprint("Press B to return to the editor.")\n'
    result['ssslot004.ref'] = b'sscode004.lua\n'
    blue = (ROOT/'examples/blue.lua').read_bytes().replace(b'@@TOKEN@@',b'INCLUDED EXAMPLE')
    result['sscode005.lua'] = blue
    result['ssslot005.ref'] = b'sscode005.lua\n'
    result['ssdemo-blue.lua'] = blue
    result['.nx_save_meta.bin'] = portable_metadata()
    assert len(result)==274
    assert not any((n.startswith('.') and n!='.nx_save_meta.bin') or n.endswith(('.bak','.new')) for n in result)
    return result


def package_save(base,output=None):
    files = starter_files(base)
    out = Path(output) if output else ROOT/'dist'
    out.mkdir(parents=True,exist_ok=True)
    target = out/'Seedsow-Lua-Editor-Save.zip'
    if Path(base).resolve()==target.resolve():
        raise ValueError('Choose an output folder different from the input save.')
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,data in sorted(files.items()):
            info = zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644<<16
            archive.writestr(info,data)
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None and set(archive.namelist())==set(files)
        assert all(archive.read(n)==b for n,b in files.items())
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix('.zip.sha256').write_text(digest+'  '+target.name+'\n',encoding='ascii')
    manifest = {'kind':'ready-to-restore-editor-save','archive':target.name,'sha256':digest,
                'personal_account_metadata_included':False,'portable_restore_metadata':True,
                'user_programs_included':False,
                'included_examples':[4,5], 'game':'Seedsow Lullaby US demo 1.0.0',
                'save_files':{n:hashlib.sha256(b).hexdigest() for n,b in sorted(files.items())}}
    target.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return {'zip':str(target.resolve()),'sha256':digest,'files':len(files),'bytes':target.stat().st_size}


if __name__=='__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',type=Path,required=True,help='Reviewed starter editor save ZIP')
    p.add_argument('--output',type=Path)
    args = p.parse_args()
    print(json.dumps(package_save(args.base,args.output),indent=2))
