"""Build a private editor installation ZIP from the owner's compatible backup."""
import argparse
import hashlib
import json
import re
import secrets
import struct
import sys
import zipfile
import zlib
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / 'tools'))
from indexed_save import IndexedSave, Edit, string, u32
from asb import encode_asb
from save_globals import replace_fixed_title


def core_source():
    return (b'local W=(function()\n' + (HERE/'storage.lua').read_bytes() + b'\nend)()\n'
            + b'local Transfer=(function()\n' + (HERE/'transfer.lua').read_bytes() + b'\nend)()\n'
            + b'local Input=(function()\n' + (HERE/'input.lua').read_bytes() + b'\nend)()\n'
            + (HERE/'editor.lua').read_bytes())


def load_backup(path):
    """Read flat JKSV files, also accepting one enclosing backup directory."""
    with zipfile.ZipFile(path) as archive:
        entries = [i for i in archive.infolist() if not i.is_dir()]
        if not entries or sum(i.file_size for i in entries) > 256 * 1024 * 1024:
            raise ValueError('Backup is empty or exceeds 256 MiB.')
        parts = [PurePosixPath(i.filename.replace('\\', '/')) for i in entries]
        if any(p.is_absolute() or '..' in p.parts or ':' in str(p) for p in parts):
            raise ValueError('Backup contains an unsafe filename.')
        nested = all(len(p.parts) == 2 for p in parts) and len({p.parts[0] for p in parts}) == 1
        if not nested and any(len(p.parts) != 1 for p in parts):
            raise ValueError('ZIP one backup folder, not a collection of backups.')
        files = {}
        for item, part in zip(entries, parts):
            name = part.name
            if name in files or not re.fullmatch(r'[A-Za-z0-9_.-]+', name) or name in ('.', '..'):
                raise ValueError('Duplicate or unsupported backup filename: ' + name)
            files[name] = archive.read(item)
    if not {'saveg.dat', 'save0001.dat', 'save0001.png', 'save0001_s.png'} <= files.keys():
        raise ValueError('Expected a Seedsow demo backup containing manual slot 1 and its thumbnails.')
    IndexedSave(files['saveg.dat'])
    return files


def launcher_template(files):
    """Accept existing editor launchers or the established clean-demo autosave state."""
    if 'ssseed001.bin' in files:
        template = IndexedSave(files['ssseed001.bin'])
        caret = template.groups[template.groups[0][3]]
        if (template.lp(caret[3]) != b'save:/sed01.asb'
                or struct.unpack_from('<I', template.fields, caret[1])[0] != 0
                or struct.unpack_from('<I', template.fields, caret[4])[0] != 1):
            raise ValueError('The existing editor launcher is not recognized.')
        return template
    if 'autosave.dat' not in files:
        raise ValueError('A clean-demo backup must also contain autosave.dat.')
    save = IndexedSave(files['autosave.dat'])
    root = save.groups[0]
    caret = save.groups[root[3]]
    command = save.groups[caret[8]]
    expected = u32(1) + string('function') + string('clickEnd')
    try:
        if (save.lp(caret[3]) != b'system/script.asb' or save.lp(command[3]) != b'calllua'
                or struct.unpack_from('<I', save.fields, caret[2])[0] != 0):
            raise ValueError('Unrecognized autosave state.')
        edits = [Edit(caret[1], u32(1), u32(0)),
                 Edit(caret[3], string('system/script.asb'), string('save:/sed01.asb')),
                 Edit(caret[4], u32(42), u32(1)), Edit(command[2], u32(73), u32(0)),
                 Edit(command[3], string('calllua'), string('')), Edit(command[4], expected, u32(0))]
        for key, name in {34:'vsync', 38:'keyClickStart', 50:'keyClickEnd',
                          69:'store', 70:'restore', 80:'exskip_end'}.items():
            edits.append(Edit(root[key], string(name), string('')))
        return IndexedSave(save.apply(edits))
    except (KeyError, ValueError) as error:
        raise ValueError('Unsupported initial autosave layout. The tested reference is demo 1.0.0 '
                         'from the US eShop at its initial title-screen autosave, with a manual save in slot 1. '
                         'Your input ZIP has not been changed.') from error


def bootstrap(number, checksum, build_id):
    name = f'seedsow_editor_boot_{number:03d}'
    config = {'build_id': build_id}
    if number == 2:
        config['receive'] = True
    if number >= 4:
        config['run_slot'] = number
    lua_config = '{' + ','.join(k+'='+('true' if v is True else json.dumps(v)) for k,v in config.items()) + '}'
    source = '''function %s(engine)
    local base=engine:var("s.savepath")
    local errors={}
    for i=1,3 do
        local name="ssedit"..i..".lua"
        local ok,source=pcall(function() return engine:file(base.."/"..name) end)
        if ok and type(source)=="string" then
            local a,b=1,0
            for at=1,#source do a=(a+source:byte(at))%%65521; b=(b+a)%%65521 end
            if b*65536+a==%d then
                local chunk,why=loadstring(source,"@"..base.."/"..name)
                if chunk then
                    local loaded,module=pcall(chunk)
                    if loaded and type(module)=="table" and type(module.start)=="function" then
                        _G.seedsow_editor=module
                        module.start(engine,%s,source)
                        return
                    end
                    errors[#errors+1]=tostring(module)
                else errors[#errors+1]=tostring(why) end
            else errors[#errors+1]=name..": checksum mismatch" end
        else errors[#errors+1]=name..": unavailable" end
    end
    engine:tag{"dialog",title="Editor recovery",textfield="t.ssedit_recovery",message=table.concat(errors,"\\n"),textfieldsize="2048"}
end''' % (name, checksum, lua_config)
    return encode_asb([('lua', {'script':source}), ('calllua', {'function':name}),
                       ('wait', {'time':'0', 'input':'0'}), ('stop', {})])


def build(base, output=None, replace_slots=False):
    base = Path(base).resolve()
    files = load_backup(base)
    existing = 'ssseed001.bin' in files
    if not existing and not replace_slots:
        raise ValueError('First installation replaces slots 1–3. Back up your saves, then enable '
                         'the installation checkbox or pass --replace-slots.')
    template = launcher_template(files)
    caret = template.groups[template.groups[0][3]]
    core = core_source()
    checksum = zlib.adler32(core)
    build_id = secrets.token_hex(4)
    entry_label = None
    menu = IndexedSave(files['saveg.dat'])
    for title in (b'LUA EDITOR V1', b'LUA EDITOR V2', b'LUA EDITOR V3', b'"Yoko, stop!"'):
        if menu.fields.count(title) == 1:
            if title != b'LUA EDITOR V3':
                files['saveg.dat'] = replace_fixed_title(files['saveg.dat'], title, b'LUA EDITOR V3')
            entry_label = 'LUA EDITOR V3'
            break
    for slot in range(1,121):
        script = f'sed{slot:02d}.asb' if slot <= 3 else f'ss{slot:03d}.asb'
        data = template.apply([Edit(caret[3], string('save:/sed01.asb'), string('save:/'+script))])
        files[f'ssseed{slot:03d}.bin'] = data
        launch = bootstrap(slot, checksum, build_id)
        files[script] = launch
        if slot <= 3:
            files[f'ssboot{slot}.bin'] = launch
            files[f'ssedit{slot}.lua'] = core
            files[f'save{slot:04d}.dat'] = data
            for suffix in ('.png', '_s.png'):
                files[f'save{slot:04d}{suffix}'] = files[f'save0001{suffix}']
    files['ssethumb.png'] = files['save0001_s.png']
    examples = {4: b'print("Hello from a persistent Lua slot!")\nprint("Press B to return to the editor.")\n',
                5: (ROOT/'examples/blue.lua').read_bytes().replace(b'@@TOKEN@@', b'LOCAL CONTROL / included example')}
    for slot, source in examples.items():
        if f'save{slot:04d}.dat' not in files:
            files[f'save{slot:04d}.dat'] = files[f'ssseed{slot:03d}.bin']
            files[f'sscode{slot:03d}.lua'] = source
            files[f'ssslot{slot:03d}.ref'] = f'sscode{slot:03d}.lua\n'.encode()
            for suffix in ('.png', '_s.png'):
                files[f'save{slot:04d}{suffix}'] = files[f'save0001{suffix}']
    out = (Path(output) if output else ROOT/'build/installer'/build_id).resolve()
    target = out/'Seedsow-Lua-Editor-Save.zip'
    if target.exists() or (out/'manifest.json').exists():
        raise ValueError('Output already contains a build. Choose a new output folder.')
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    manifest = {'build_id':build_id, 'version':3, 'entry_label':entry_label,
                'source_sha256':{}, 'input_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),
                'runtime_core_adler32':checksum, 'editor_slots':[1,2,3], 'user_slots':[4,120],
                'console_tested':False, 'save_zip':str(target),
                'save_files':{n:hashlib.sha256(b).hexdigest() for n,b in files.items()},
                'note':'Private save package; do not include it in a public source release.'}
    (out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True, help='Your own compatible backup ZIP')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--replace-slots', action='store_true', help='Allow first installation into slots 1–3')
    args = parser.parse_args()
    try:
        info = build(args.base, args.output, args.replace_slots)
        print(json.dumps({k:info[k] for k in ('build_id','save_zip','entry_label')}, indent=2))
    except (ValueError, KeyError, zipfile.BadZipFile, OSError) as error:
        parser.exit(1, 'Build failed: '+str(error)+'\n')
