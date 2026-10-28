"""Compose the current editor or read the frozen compatibility core."""
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECOVERY_SHA256 = '6e1e9664ed818c1dab5029fc36c1b2cc4358e13d75cdac4336363f1e29ed1d73'


def recovery_source():
    data = (HERE/'recovery_v3.lua').read_bytes()
    if hashlib.sha256(data).hexdigest() != RECOVERY_SHA256:
        raise ValueError('Reviewed recovery core changed; restore editor/recovery_v3.lua.')
    return data


def current_source():
    modules = (('W', 'storage.lua'), ('Transfer', 'transfer.lua'), ('Input', 'input.lua'),
               ('Navigation', 'navigation.lua'), ('Controls', 'controls.lua'))
    parts = [b'local '+name.encode()+b'=(function()\n'+(HERE/file).read_bytes()+b'\nend)()\n'
             for name, file in modules]
    return (b''.join(parts)+(HERE/'editor.lua').read_bytes()).replace(b'\r\n', b'\n')


def core_source():
    return b'local SIDE_SLOT=nil\n'+current_source()
