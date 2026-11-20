"""Checks the distributed board image and rejection of damaged/wrong-chip data."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('uf2check', ROOT / 'tools/check_pico2w_firmware.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class FirmwareTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((checker.ROOT / 'build.json').read_text())
        self.data = (checker.ROOT / self.manifest['file']).read_bytes()

    def test_included_image(self):
        checker.validate(self.data, self.manifest)

    def test_corrupt_download(self):
        with self.assertRaises(ValueError):
            checker.validate(self.data[:-1], self.manifest)

    def test_wrong_chip_even_with_recomputed_hash(self):
        data = bytearray(self.data)
        for i in range(0, len(data), 512):
            struct.pack_into('<I', data, i + 28, 0xE48BFF56)
        manifest = dict(self.manifest, sha256=hashlib.sha256(data).hexdigest())
        with self.assertRaises(ValueError):
            checker.validate(data, manifest)

    def test_missing_program_block_even_with_recomputed_hash(self):
        data = self.data[:-512]
        manifest = dict(self.manifest, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        with self.assertRaises(ValueError):
            checker.validate(data, manifest)
