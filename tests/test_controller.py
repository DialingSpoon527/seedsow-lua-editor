"""Controller packet and failure checks using simulated UART and HTTP devices."""

import contextlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import struct
import sys
import tempfile
import threading
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'pc'))
import controller_protocol as protocol
import pico_uart
import send_controller as sender


class FakeSerial:
    def __init__(self, *args, **kwargs):
        self.is_open = True
        self.in_waiting = 0
        self.frames = []
        self.short_write = False

    def write(self, frame):
        self.frames.append(frame)
        return len(frame) - int(self.short_write)

    def read(self, count):
        return b''

    def close(self):
        self.is_open = False


class ControllerTests(unittest.TestCase):
    def test_uart_full_file_roundtrip_from_clock_edges(self):
        board = FakeSerial()
        module = types.SimpleNamespace(Serial=lambda *a, **kw: board, SerialException=OSError)
        # Exercise every byte value, including zero, alongside a plausible Lua file.
        source = b'print("controller test")\n' + bytes(range(256))
        with tempfile.TemporaryDirectory() as temp:
            filename = Path(temp) / 'input.lua'
            filename.write_bytes(source)
            with mock.patch.dict(sys.modules, {'serial': module}), mock.patch.object(sender.time, 'sleep'), contextlib.redirect_stdout(io.StringIO()):
                result = sender.main(['--serial-port', 'fake', 'send', str(filename), '--slot', '20', '--name', 'check.lua', '--ready'])
        self.assertEqual(result, 0)
        self.assertFalse(board.is_open)
        clock = False
        nibbles = []
        for frame in board.frames:
            self.assertEqual(frame[:4], bytes([0xAA, 3, 8, 0]))
            self.assertEqual(len(frame), 13)
            self.assertEqual(frame[-1], sum(frame[:-1]) & 255)
            mask, hat, lx, ly, rx, ry, imu_count = struct.unpack('<HBBBBBB', frame[4:-1])
            self.assertEqual((hat, lx, ly, rx, ry, imu_count), (8, 128, 128, 128, 128, 0))
            new_clock = bool(mask & (1 << 5))
            if new_clock != clock:
                # Firmware bits A=2, B=1, X=3, Y=0; receiver nibble order A,B,X,Y.
                nibbles.append(sum((1 << bit) for bit, wire_bit in enumerate((2, 1, 3, 0)) if mask & (1 << wire_bit)))
                clock = new_clock
        received = bytes((nibbles[at] << 4) | nibbles[at + 1] for at in range(0, len(nibbles), 2))
        self.assertEqual(protocol.unpack(received), ('P020_check.lua', source))
        self.assertEqual(board.frames[-1], pico_uart.report([]))

    def test_partial_uart_report_is_not_replayed(self):
        board = FakeSerial()
        board.short_write = True
        module = types.SimpleNamespace(Serial=lambda *a, **kw: board, SerialException=OSError)
        with mock.patch.dict(sys.modules, {'serial': module}):
            controller = pico_uart.PicoUART('fake')
            with self.assertRaisesRegex(OSError, 'Incomplete UART'):
                controller.set_buttons(['R'])
        self.assertEqual(len(board.frames), 1)

    def test_recovery_releases_direction_after_lost_press_reply(self):
        controller = sender.Controller({'host': 'localhost'})
        calls = []

        def request(endpoint, body=None):
            calls.append((endpoint, body))
            if endpoint == '/press':
                raise TimeoutError('reply lost')
            return {'ok': True}

        with mock.patch.object(controller, 'request', side_effect=request):
            with self.assertRaises(TimeoutError):
                controller.set_buttons(['DPAD_UP'])
            controller.clear()
        self.assertEqual(sum(endpoint == '/press' for endpoint, _ in calls), 1)
        released = {button for endpoint, data in calls if endpoint == '/release' for button in data['buttons']}
        self.assertTrue(set(sender.ALL_BUTTONS) | set(pico_uart.HATS) <= released)
        self.assertTrue(all(len(data['buttons']) <= 8 for _, data in calls))

    def test_invalid_destination_never_opens_serial(self):
        with mock.patch.object(sender, 'PicoUART') as serial, contextlib.redirect_stderr(io.StringIO()):
            result = sender.main(['--serial-port', 'fake', 'send', 'unused', '--slot', '1', '--ready'])
        self.assertEqual(result, 1)
        serial.assert_not_called()

    def test_interrupt_releases_buttons_and_closes_serial(self):
        board = FakeSerial()
        module = types.SimpleNamespace(Serial=lambda *a, **kw: board, SerialException=OSError)
        with mock.patch.dict(sys.modules, {'serial': module}), mock.patch.object(sender.time, 'sleep', side_effect=[KeyboardInterrupt(), None]), contextlib.redirect_stderr(io.StringIO()):
            result = sender.main(['--serial-port', 'fake', 'tap', 'A', '--ready'])
        self.assertEqual(result, 130)
        self.assertFalse(board.is_open)
        self.assertEqual(board.frames[-1], pico_uart.report([]))

    def test_http_response_validation_and_no_retry(self):
        class Device(BaseHTTPRequestHandler):
            calls = 0
            status = 200
            body = b'{"ok":true}'

            def do_GET(self):
                Device.calls += 1
                self.send_response(Device.status)
                self.send_header('Content-Length', str(len(Device.body)))
                self.end_headers()
                self.wfile.write(Device.body)

            def log_message(self, *args):
                pass

        with ThreadingHTTPServer(('127.0.0.1', 0), Device) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                controller = sender.Controller({'host': '127.0.0.1', 'port': server.server_port})
                self.assertEqual(controller.request('/status'), {'ok': True})
                for status, body in [(401, b''), (404, b''), (302, b''), (200, b'bad JSON'), (200, b'x' * 4097), (200, b'{"ok":false}')]:
                    with self.subTest(status=status, body=body[:20]):
                        Device.status, Device.body = status, body
                        before = Device.calls
                        with self.assertRaises(ValueError):
                            controller.request('/status')
                        self.assertEqual(Device.calls, before + 1)
            finally:
                server.shutdown()
                thread.join()


if __name__ == '__main__':
    unittest.main()
