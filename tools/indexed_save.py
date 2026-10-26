"""Read/edit Artemis 1002/1003 saves while preserving their field index.

The final uint32 points to a two-level index. Its outer keys are object
start offsets; its inner maps give field IDs and absolute body offsets.
Observed in the user's save and confirmed against the supplied native reader.
"""
from dataclasses import dataclass
import struct
import zlib


def u32(value):
    return struct.pack('<I', value)


def string(value):
    if isinstance(value, str):
        value = value.encode('utf-8')
    return u32(len(value)) + value


@dataclass(frozen=True)
class Edit:
    start: int
    before: bytes
    after: bytes


class IndexedSave:
    def __init__(self, data):
        self.magic, self.version, size = struct.unpack_from('<4sII', data)
        if self.magic not in (b'BOWS', b'BOWG', b'BOWX') or self.version not in (1002, 1003):
            raise ValueError('Unsupported save format')
        obj = zlib.decompressobj()
        self.body = obj.decompress(data[12:]) + obj.flush()
        if not obj.eof or obj.unused_data or len(self.body) != size:
            raise ValueError('Invalid compressed body')
        self.index_start = struct.unpack_from('<I', self.body, len(self.body) - 4)[0]
        if not 0 <= self.index_start < len(self.body) - 4:
            raise ValueError('Index pointer outside body')
        self.fields = self.body[:self.index_start]
        cursor = self.index_start

        def read():
            nonlocal cursor
            if cursor + 4 > len(self.body) - 4:
                raise ValueError('Truncated index')
            value = struct.unpack_from('<I', self.body, cursor)[0]
            cursor += 4
            return value

        self.groups = {}
        count = read()
        if count > 100000:
            raise ValueError('Implausible index group count')
        for _ in range(count):
            base, length = read(), read()
            if base in self.groups or base >= self.index_start or length > 100000:
                raise ValueError('Invalid index group')
            entries = {}
            for _ in range(length):
                key, offset = read(), read()
                if key in entries or not 0 <= offset < self.index_start:
                    raise ValueError('Invalid index field')
                entries[key] = offset
            self.groups[base] = entries
        if cursor != len(self.body) - 4 or 0 not in self.groups:
            raise ValueError('Index does not end at trailer')
        if self.make_body(self.fields, self.groups) != self.body:
            raise ValueError('Index round trip differs')

    @staticmethod
    def make_body(fields, groups):
        index = bytearray(u32(len(groups)))
        for base, entries in groups.items():
            index += u32(base) + u32(len(entries))
            for key, offset in entries.items():
                index += u32(key) + u32(offset)
        return fields + index + u32(len(fields))

    def lp(self, offset):
        size = struct.unpack_from('<I', self.fields, offset)[0]
        if offset + 4 + size > len(self.fields):
            raise ValueError('String outside fields')
        return self.fields[offset + 4:offset + 4 + size]

    def apply(self, edits):
        edits = sorted(edits, key=lambda item: item.start)
        previous_end = 0
        parts = []
        for edit in edits:
            end = edit.start + len(edit.before)
            if not edit.before or edit.start < previous_end or end > len(self.fields):
                raise ValueError('Overlapping or invalid field edit')
            if self.fields[edit.start:end] != edit.before:
                raise ValueError(f'Unexpected field bytes at {edit.start}')
            parts += [self.fields[previous_end:edit.start], edit.after]
            previous_end = end
        parts.append(self.fields[previous_end:])
        fields = b''.join(parts)

        def relocate(offset):
            delta = 0
            for edit in edits:
                if offset <= edit.start:
                    break
                end = edit.start + len(edit.before)
                if offset < end:
                    raise ValueError(f'Indexed offset {offset} points into an edited field')
                delta += len(edit.after) - len(edit.before)
            return offset + delta

        groups = {relocate(base): {key: relocate(offset) for key, offset in entries.items()}
                  for base, entries in self.groups.items()}
        if len(groups) != len(self.groups):
            raise ValueError('Object index collision')
        body = self.make_body(fields, groups)
        result = self.magic + u32(self.version) + u32(len(body)) + zlib.compress(body, 9)
        check = IndexedSave(result)
        if check.fields != fields or check.groups != groups:
            raise ValueError('Edited index failed round trip')
        return result
