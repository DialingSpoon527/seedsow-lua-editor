"""Put a configured uploader in the standalone UF2; never access a board."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'pc'))
from controller_protocol import destination, pack
from make_sheet import ask, generate

MARKER = b'S2PICO2WCONFIG01'
RESERVE = 8192


def configure(template, packet):
    if len(packet) > RESERVE - 24 or not template or len(template) % 512:
        raise ValueError('Packet or UF2 length is invalid.')
    result = bytearray(template)
    mapping = {}
    for offset in range(0, len(result), 512):
        a, b, flags, address, length, number, count, family = struct.unpack_from('<8I', result, offset)
        if (a, b, struct.unpack_from('<I', result, offset + 508)[0]) != (0x0A324655, 0x9E5D5157, 0x0AB16F30):
            raise ValueError('Invalid UF2 block.')
        if family == 0xE48BFF57:
            continue
        if flags != 0x2000 or family != 0xE48BFF59 or not 0 < length <= 476:
            raise ValueError('Expected an RP2350 ARM Secure image.')
        for i in range(length):
            if address + i in mapping:
                raise ValueError('Overlapping UF2 blocks.')
            mapping[address + i] = offset + 32 + i
    addresses = sorted(mapping)
    if not addresses or addresses != list(range(addresses[0], addresses[-1] + 1)):
        raise ValueError('Noncontiguous image.')
    payload = bytes(result[mapping[a]] for a in addresses)
    if payload.count(MARKER) != 1:
        raise ValueError('Standalone configuration marker missing or ambiguous.')
    start = payload.index(MARKER)
    if start + RESERVE > len(payload) or any(payload[start + 16:start + RESERVE]):
        raise ValueError('Use an original blank template, not a configured image.')
    config = MARKER + struct.pack('<II', len(packet), zlib.crc32(packet)) + packet
    config += bytes(RESERVE - len(config))
    for i, byte in enumerate(config):
        result[mapping[addresses[0] + start + i]] = byte
    return bytes(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ip')
    parser.add_argument('--port', type=int)
    parser.add_argument('--slot', type=int, help='Unused Artemis launcher slot')
    parser.add_argument('--uploader-slot', type=int, help='Different unused uploader slot')
    parser.add_argument('--name', default='artemis-uploader.lua')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'build/pico2w-standalone')
    args = parser.parse_args()
    values = (args.ip, args.port, args.slot, args.uploader_slot)
    if all(v is None for v in values):
        print('Check TWO UNUSED slots and an unused artemis-uploader.lua filename first.\nNo console connection is made.\n')
        values = (ask('Computer LAN IPv4 address'), ask('TCP port (for example 39000)', int),
                  ask('Unused Artemis launcher slot', int), ask('Different unused uploader slot', int))
    elif any(v is None for v in values):
        parser.error('Supply all four settings or omit them for guided setup.')
    destination(args.name, values[3])
    target = args.output_dir.resolve() / 'pico2w-standalone-CONFIGURED.uf2'
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        raise ValueError('Output folder is not empty. Preserve the earlier files and choose a new --output-dir.')
    folder = ROOT / 'firmware/standalone'
    manifest = json.loads((folder / 'template.json').read_text())
    template = (folder / manifest['file']).read_bytes()
    if hashlib.sha256(template).hexdigest() != manifest['sha256']:
        raise ValueError('Standalone template checksum differs.')
    config, out = generate(*values, args.output_dir)
    source = (out / 'TYPE_THIS_EXACT.lua').read_bytes()
    packet = pack(destination(args.name, values[3]) + '_' + args.name, source)
    image = configure(template, packet)
    target.write_bytes(image)
    settings = dict(config, filename=args.name, packet_bytes=len(packet),
                    firmware_sha256=hashlib.sha256(image).hexdigest(),
                    template_sha256=manifest['sha256'], hardware_tested=False,
                    minimum_transfer_minutes=round(len(packet) * 2 * .3 / 60, 1))
    (out / 'pico2w-standalone-settings.json').write_text(json.dumps(settings, indent=2) + '\n')
    print(f'\nCreated: {target}\nUploader slot {values[3]}; Artemis slot {values[2]}.')
    print(f'Allow at least {settings["minimum_transfer_minutes"]} minutes for controller transfer.')
    print('Flash ONLY the CONFIGURED UF2. Follow docs/09-pico2w-standalone.md. Keep build files private.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, EOFError, KeyboardInterrupt) as error:
        raise SystemExit('Setup stopped: ' + str(error))
