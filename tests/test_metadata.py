"""Target-aware metadata must not inherit the historical starter's identity."""
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/'tools'))
from jksv_metadata import portable_account_metadata


class TargetMetadata(unittest.TestCase):
    def test_explicit_distinct_target_ids_sizes_and_blank_personal_fields(self):
        data = portable_account_metadata(0x0100000000001000, owner_id=0x0100000000002000,
                                         data_size=8*1024*1024, journal_size=1024*1024)
        self.assertEqual(len(data), 86)
        self.assertEqual(struct.unpack_from('<Q', data, 5)[0], 0x0100000000001000)
        self.assertEqual(struct.unpack_from('<Q', data, 41)[0], 0x0100000000002000)
        self.assertEqual(struct.unpack_from('<qq', data, 61), (8*1024*1024, 1024*1024))
        for first, last in ((13, 29), (49, 57), (77, 85)):
            self.assertEqual(data[first:last], bytes(last-first))

    def test_invalid_ids_and_sizes_are_rejected(self):
        valid = dict(application_id=1, owner_id=2, data_size=4096, journal_size=0)
        for field, values in {'application_id': (0, -1, 2**64, True, '1'),
                              'owner_id': (0, -1, 2**64),
                              'data_size': (0, -1, 2**63),
                              'journal_size': (-1, 2**63, 1.5)}.items():
            for value in values:
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    portable_account_metadata(**dict(valid, **{field: value}))

    def test_no_implicit_title_or_size_defaults(self):
        with self.assertRaises(TypeError):
            portable_account_metadata()
        with self.assertRaises(TypeError):
            portable_account_metadata(1, owner_id=1)


if __name__ == '__main__':
    unittest.main()
