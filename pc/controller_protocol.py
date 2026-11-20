"""Data packets and controller symbols; no source execution on the PC/Pi."""
import re
import struct
import zlib

MAX_BYTES=1048576
BUTTONS=('A','B','X','Y')

def destination(name,slot=None):
    if not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}',name):
        raise ValueError('Filename must be 1–64 ASCII letters, digits, _, - or .')
    n=name.lower()
    if n=='saveg.dat' or re.match(r'^save000[123][.]',n) or n.startswith(('ssedit','ssseed','ssboot','ssethumb','sed01.','sed02.','sed03.')) or re.fullmatch(r'ss\d{3}\.asb',n):
        raise ValueError('Protected editor filename; choose a user filename.')
    if slot is None:return 'F000'
    if isinstance(slot,bool) or not isinstance(slot,int) or not 4<=slot<=120:
        raise ValueError('Choose a user slot from 4 to 120.')
    return f'P{slot:03d}'

def pack(name,source):
    if isinstance(source,str):source=source.encode('utf-8')
    if not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.-]{0,71}',name):raise ValueError('Use a plain filename, at most 72 ASCII characters')
    if len(source)>MAX_BYTES:raise ValueError('Program exceeds 1 MiB')
    encoded=name.encode('ascii')
    return b'SSE2\x01'+struct.pack('<II',len(source),zlib.adler32(source))+bytes([len(encoded)])+encoded+source

def unpack(packet):
    if len(packet)<14 or packet[:5]!=b'SSE2\x01':raise ValueError('Invalid packet')
    size,checksum=struct.unpack_from('<II',packet,5);length=packet[13]
    if size>MAX_BYTES or length<1 or length>72 or len(packet)!=14+length+size:raise ValueError('Invalid packet length')
    name=packet[14:14+length].decode('ascii');source=packet[14+length:]
    if pack(name,source)!=packet:raise ValueError('Checksum or packet mismatch')
    return name,source

def symbols(packet):
    for byte in packet:
        yield byte>>4
        yield byte&15

def macro(packet,prepare=.05,hold=.10):
    unpack(packet)
    if not .02<=prepare<=1 or not .04<=hold<=2:raise ValueError('Timing outside supported limits')
    lines=['1.0s'];clock=False
    for nibble in symbols(packet):
        faces=[button for bit,button in enumerate(BUTTONS) if nibble&(1<<bit)]
        lines.append(' '.join(faces+(['R'] if clock else [])+[f'{prepare:.3f}s']))
        clock=not clock
        lines.append(' '.join(faces+(['R'] if clock else [])+[f'{hold:.3f}s']))
    lines.append('0.5s')
    return '\n'.join(lines)+'\n'

def seconds(packet,prepare=.05,hold=.10):
    # Include the macro interpreter's observed delay at command boundaries.
    return 1.5+2*len(packet)*(prepare+hold+.04)
