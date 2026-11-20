import importlib.util
import json
from pathlib import Path
import struct
import sys
import unittest
import zlib
import hashlib

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
spec = importlib.util.spec_from_file_location('standalone_config', ROOT / 'tools/make_pico2w_standalone.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def payload(image):
    return b''.join(image[i+32:i+32+struct.unpack_from('<I', image, i+16)[0]]
                    for i in range(0, len(image), 512)
                    if struct.unpack_from('<I', image, i+28)[0] == 0xE48BFF59)


class StandaloneConfigTests(unittest.TestCase):
    def setUp(self):
        self.template = (ROOT / 'firmware/standalone/pico2w-standalone-TEMPLATE.uf2').read_bytes()
        self.packet = tool.pack('P021_artemis-uploader.lua', b'print("hello")')

    def test_only_reserved_payload_changes(self):
        image = tool.configure(self.template, self.packet)
        old, new = payload(self.template), payload(image)
        offset = old.index(tool.MARKER)
        self.assertEqual(old[:offset], new[:offset])
        self.assertEqual(old[offset+8192:], new[offset+8192:])
        self.assertEqual(new[offset:offset+16], tool.MARKER)
        self.assertEqual(struct.unpack_from('<II', new, offset+16), (len(self.packet), zlib.crc32(self.packet)))
        self.assertEqual(new[offset+24:offset+24+len(self.packet)], self.packet)
        for i in range(0, len(image), 512):
            self.assertEqual(self.template[i:i+32], image[i:i+32])
            self.assertEqual(self.template[i+508:i+512], image[i+508:i+512])

    def test_template_matches_recorded_binary_and_sources(self):
        folder = ROOT / 'firmware/standalone'
        manifest = json.loads((folder / 'template.json').read_text())
        self.assertEqual(hashlib.sha256(self.template).hexdigest(), manifest['sha256'])
        self.assertEqual(len(self.template), manifest['bytes'])
        for name, expected in manifest['source_sha256'].items():
            self.assertEqual(hashlib.sha256((folder / name).read_bytes()).hexdigest(), expected)

    def test_reconfiguration_rejected(self):
        image = tool.configure(self.template, self.packet)
        with self.assertRaises(ValueError):
            tool.configure(image, self.packet)

    def test_wrong_chip_rejected(self):
        image = bytearray(self.template)
        for i in range(0, len(image), 512):
            struct.pack_into('<I', image, i+28, 0xE48BFF56)
        with self.assertRaises(ValueError):
            tool.configure(image, self.packet)

    def test_truncated_image_and_oversize_packet_rejected(self):
        for image, packet in [(self.template[:-1], self.packet), (self.template, b'x'*8192)]:
            with self.assertRaises(ValueError):
                tool.configure(image, packet)
