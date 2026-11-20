"""Check the packaged Pico 2 W image without accessing any hardware."""
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parent.parent / 'firmware' / 'pico2w'


def validate(data, manifest):
    if len(data) != manifest['bytes'] or hashlib.sha256(data).hexdigest() != manifest['sha256']:
        raise ValueError('Firmware length/checksum differs from the build record.')
    if not data or len(data) % 512:
        raise ValueError('Incomplete UF2 blocks.')
    groups = {}
    for offset in range(0, len(data), 512):
        block = data[offset:offset + 512]
        magic0, magic1, flags, address, size, number, count, family = struct.unpack_from('<8I', block)
        if (magic0, magic1, struct.unpack_from('<I', block, 508)[0]) != (0x0A324655, 0x9E5D5157, 0x0AB16F30):
            raise ValueError('Invalid UF2 magic.')
        if not flags & 0x2000 or family not in (0xE48BFF57, 0xE48BFF59) or not 0 < size <= 476:
            raise ValueError('Unexpected UF2 family or payload.')
        if family == 0xE48BFF59 and not (0x10000000 <= address < address + size <= 0x10400000):
            raise ValueError('RP2350 program outside Pico 2 W flash.')
        # picotool adds an ignored RP2350-absolute compatibility block before
        # the independently numbered ARM image; its advertised count is two.
        if family == 0xE48BFF57:
            if flags != 0xA000 or number != 0 or count != 2:
                raise ValueError('Unexpected compatibility block.')
            continue
        seen, counts = groups.setdefault(family, (set(), set()))
        if number in seen:
            raise ValueError('Duplicate UF2 block.')
        seen.add(number)
        counts.add(count)
    if 0xE48BFF59 not in groups:
        raise ValueError('No RP2350 ARM Secure program.')
    for seen, counts in groups.values():
        if len(counts) != 1 or seen != set(range(next(iter(counts)))):
            raise ValueError('Missing UF2 blocks.')


if __name__ == '__main__':
    manifest = json.loads((ROOT / 'build.json').read_text())
    validate((ROOT / manifest['file']).read_bytes(), manifest)
    print('Pico 2 W firmware checksum and RP2350 UF2 structure verified. Hardware not tested.')
