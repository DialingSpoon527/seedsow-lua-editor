"""Encode and read the game's ASB version-0 script records."""
import struct

from indexed_save import string, u32


def encode_asb(commands):
    data = bytearray(b'ASB\0\0' + u32(len(commands)))
    for line, (name, params) in enumerate(commands, 1):
        data += u32(0) + string(name) + b'\0' + u32(line) + u32(len(params))
        for key, value in params.items():
            data += string(key) + b'\0' + string(value) + b'\0'
    return bytes(data)


def decode_asb(data):
    if data[:5] != b'ASB\0\0':
        raise ValueError('Unexpected ASB header')
    offset = 5

    def number():
        nonlocal offset
        value = struct.unpack_from('<I', data, offset)[0]
        offset += 4
        return value

    def read_string():
        nonlocal offset
        size = number()
        value = data[offset:offset + size].decode('utf-8')
        offset += size
        if data[offset] != 0:
            raise ValueError('Missing ASB string terminator')
        offset += 1
        return value

    commands = []
    for _ in range(number()):
        kind, name = number(), read_string()
        if kind == 1:
            continue  # Labels do not consume an interpreter command index.
        if kind != 0:
            raise ValueError('Unexpected ASB record kind')
        line, count = number(), number()
        params = {read_string(): read_string() for _ in range(count)}
        commands.append((name, line, params))
    if offset != len(data):
        raise ValueError('Unconsumed ASB bytes')
    return commands
