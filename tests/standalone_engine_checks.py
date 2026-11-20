"""Execute the actual firmware C scheduler through a native test DLL."""
import ctypes as c
from pathlib import Path
import sys
import unittest
import zlib

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'pc'))
import controller_protocol as protocol

class Sender(c.Structure):
    _fields_ = [('packet', c.POINTER(c.c_uint8)), ('length', c.c_size_t), ('step', c.c_size_t),
                ('deadline', c.c_uint64), ('mask', c.c_uint16), ('mode', c.c_uint),
                ('active', c.c_int), ('delivered', c.c_int), ('finished', c.c_int)]

class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = c.CDLL(sys.argv[1])
        cls.lib.sender_start.argtypes = [c.POINTER(Sender), c.c_uint, c.POINTER(c.c_uint8), c.c_size_t]
        cls.lib.sender_cancel.argtypes = [c.POINTER(Sender)]
        cls.lib.sender_report_sent.argtypes = [c.POINTER(Sender), c.c_uint64]
        cls.lib.packet_crc.argtypes = [c.POINTER(c.c_uint8), c.c_size_t]
        cls.lib.packet_crc.restype = c.c_uint32
        cls.lib.sender_mode_for_hold.argtypes = [c.c_uint64]
        cls.lib.sender_mode_for_hold.restype = c.c_uint

    def setup(self, packet=None, mode=3):
        packet = packet or protocol.pack('P021_test.lua', bytes(range(256)))
        raw = (c.c_uint8 * len(packet)).from_buffer_copy(packet)
        state = Sender()
        self.assertEqual(self.lib.sender_start(c.byref(state), mode, raw, len(packet)), 1)
        return state, raw, packet

    def test_actual_scheduler_roundtrip(self):
        s, raw, packet = self.setup()
        previous = False
        nibbles = []
        elapsed = 0
        while s.active:
            clock = bool(s.mask & 32)
            if clock != previous:
                nibbles.append(sum(1 << bit for bit, mask in enumerate([4, 2, 8, 1]) if s.mask & mask))
            previous = clock
            self.lib.sender_report_sent(c.byref(s), elapsed)
            elapsed += 10
            self.assertLess(elapsed, 300000)
        decoded = bytes((nibbles[i] << 4) | nibbles[i + 1] for i in range(0, len(nibbles), 2))
        self.assertEqual(decoded, packet)
        self.assertEqual(protocol.unpack(decoded)[1], bytes(range(256)))
        self.assertEqual(s.mask, 0)
        self.assertGreaterEqual(elapsed, len(packet) * 2 * 300)

    def test_calibration_order(self):
        s, raw, packet = self.setup(mode=2)
        seen = []
        for t in range(0, 30000, 10):
            if s.mask and (not seen or seen[-1] != s.mask):
                seen.append(s.mask)
            self.lib.sender_report_sent(c.byref(s), t)
        self.assertEqual(seen, [4, 2, 8, 1, 16, 32])
        self.assertFalse(s.active)

    def test_cancel_and_stall_release(self):
        s, raw, packet = self.setup(mode=1)
        self.assertEqual(s.mask, 48)
        self.lib.sender_cancel(c.byref(s))
        self.assertEqual((s.active, s.mask), (0, 0))
        s, raw, packet = self.setup()
        self.lib.sender_report_sent(c.byref(s), 0)
        self.lib.sender_report_sent(c.byref(s), 4000)
        self.assertEqual((s.active, s.mask), (0, 0))

    def test_malformed_packet_rejected(self):
        packet = bytearray(protocol.pack('P021_test.lua', b'hello'))
        packet[-1] ^= 1
        raw = (c.c_uint8 * len(packet)).from_buffer_copy(packet)
        self.assertEqual(self.lib.sender_start(c.byref(Sender()), 3, raw, len(packet)), 0)
        self.assertEqual(self.lib.packet_crc(raw, len(packet)), zlib.crc32(packet))

    def test_join_then_a_and_hold_thresholds(self):
        s, raw, packet = self.setup(mode=1)
        seen = []
        for t in range(0, 3000, 10):
            if not seen or seen[-1] != s.mask:
                seen.append(s.mask)
            self.lib.sender_report_sent(c.byref(s), t)
        self.assertEqual(seen, [48, 0, 4, 0])
        for ms, mode in [(0, 0), (99, 0), (100, 1), (999, 1), (1000, 2), (3499, 2), (3500, 3), (5000, 3)]:
            self.assertEqual(self.lib.sender_mode_for_hold(ms), mode)

    def test_idle_no_input_and_no_overlapping_start(self):
        s = Sender()
        self.lib.sender_report_sent(c.byref(s), 999999)
        self.assertEqual((s.active, s.mask), (0, 0))
        s, raw, packet = self.setup(mode=1)
        self.assertEqual(self.lib.sender_start(c.byref(s), 3, raw, len(packet)), 0)
        self.assertEqual(s.mode, 1)

if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]], verbosity=2)
