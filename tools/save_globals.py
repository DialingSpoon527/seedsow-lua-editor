"""Read the length-prefixed global-variable payload inside a BOWG save.

The outer object index doesn't describe lengths inside these variable values.
Each value can itself contain a Pluto-serialized Lua object with more lengths.
"""
import struct
from indexed_save import IndexedSave


def read_globals(data):
    save = IndexedSave(data)
    if save.magic != b'BOWG' or 2 not in save.groups[0]:
        raise ValueError('Unsupported global save layout')
    cursor = save.groups[0][2]
    later = [offset for group in save.groups.values() for offset in group.values() if offset > cursor]
    end = min(later, default=len(save.fields))

    def number():
        nonlocal cursor
        if cursor+4 > end:
            raise ValueError('Truncated global-variable length')
        result = struct.unpack_from('<I', save.fields, cursor)[0]
        cursor += 4
        return result

    def blob():
        nonlocal cursor
        size = number()
        if cursor+size > end:
            raise ValueError('Global variable value extends beyond its payload')
        result = save.fields[cursor:cursor+size]
        cursor += size
        return result

    count = number()
    if count > 100000:
        raise ValueError('Implausible global-variable count')
    result = {}
    for _ in range(count):
        name = blob().decode('utf-8')
        if name in result:
            raise ValueError('Duplicate global-variable name')
        result[name] = blob()
    if cursor != end:
        raise ValueError('Unconsumed global-variable payload')
    return result


def replace_fixed_title(data, old, new):
    if len(old) != len(new):
        raise ValueError('Embedded title replacement must preserve its byte length')
    save = IndexedSave(data)
    if save.fields.count(old) != 1:
        raise ValueError('Expected one matching embedded title')
    at = save.fields.index(old)
    if at < 8 or struct.unpack_from('<Q', save.fields, at-8)[0] != len(old):
        raise ValueError('Unexpected embedded title length')
    before = read_globals(data)
    from indexed_save import Edit
    result = save.apply([Edit(at, old, new)])
    after_save = IndexedSave(result)
    after = read_globals(result)
    if after_save.groups != save.groups or len(after_save.fields) != len(save.fields):
        raise ValueError('Fixed-width replacement moved the outer layout')
    if set(before) != set(after) or any(len(after[name]) != len(value) for name, value in before.items()):
        raise ValueError('Global-variable sizes changed')
    changed = [name for name, value in before.items() if after[name] != value]
    if changed != ['g.system'] or before['g.system'].replace(old, new, 1) != after['g.system']:
        raise ValueError('Unexpected global data changed')
    return result
