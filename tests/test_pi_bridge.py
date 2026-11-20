"""Pi bridge regressions with fake Bluetooth state and localhost HTTP only."""

import base64
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock
from urllib.error import HTTPError
from urllib.request import Request, build_opener, ProxyHandler

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'pi'), str(ROOT / 'pc')]
import bluez_compat
from pi_bridge import Bridge, make_server
from controller_protocol import unpack


class FakeNX:
    def __init__(self):
        self.state = {0: {'state': 'connected', 'finished_macros': [], 'player_number': 1}}
        self.programs = []
        self.stopped = []
        self.selected = None
        self.finished = True
        self.stop_entered = threading.Event()
        self.allow_stop = threading.Event()
        self.allow_stop.set()

    def macro(self, controller, program, block=False):
        self.programs.append(program)
        mid = str(len(self.programs))
        if self.finished:
            self.state[controller]['finished_macros'].append(mid)
        return mid

    def stop_macro(self, controller, mid, block=False):
        self.stop_entered.set()
        if not self.allow_stop.wait(2):
            raise RuntimeError('test stop blocked')
        self.stopped.append(mid)

    def get_available_adapters(self):
        return ['/org/bluez/hci1']

    def create_controller(self, kind, adapter_path=None):
        self.selected = adapter_path
        return 0

    def clear_macros(self, controller):
        raise AssertionError('A transfer cancellation must stop that specific macro')


class PiTransferTests(unittest.TestCase):
    def setUp(self):
        self.nx = FakeNX()
        self.bridge = Bridge(self.nx, None)
        self.bridge.controller = 0

    def wait_for_idle(self):
        deadline = time.monotonic() + 2
        while self.bridge.status()['transfer'] is not None and time.monotonic() < deadline:
            time.sleep(.005)
        self.assertIsNone(self.bridge.status()['transfer'])

    def test_binary_file_reaches_unchanged_receiver_packet(self):
        source = bytes(range(256))
        self.bridge.send('test.lua', source, slot=20)
        self.wait_for_idle()
        nibbles = []
        for line in self.nx.programs[0].splitlines()[2:-1:2]:
            buttons = line.split()[:-1]
            nibbles.append(sum(1 << bit for bit, button in enumerate(('A', 'B', 'X', 'Y')) if button in buttons))
        packet = bytes((nibbles[i] << 4) | nibbles[i + 1] for i in range(0, len(nibbles), 2))
        self.assertEqual(unpack(packet), ('P020_test.lua', source))
        self.assertEqual(self.bridge.last['state'], 'input sent')
        self.assertFalse(self.bridge.status()['console_acknowledged'])

    def test_stop_blocks_replacement_until_worker_queues_cancellation(self):
        self.nx.finished = False
        with mock.patch('pi_bridge.threading.Thread') as thread:
            self.bridge.send('old.lua', b'old', slot=20)
            finish_worker = thread.call_args.kwargs['target']
            snapshot = self.bridge.status()
            self.bridge.stop()
            self.assertIsNotNone(self.bridge.transfer)
            self.assertEqual(snapshot['transfer']['state'], 'sending')
            with self.assertRaisesRegex(ValueError, 'already active'):
                self.bridge.send('new.lua', b'new', slot=21)
            finish_worker()
        self.assertIsNone(self.bridge.transfer)
        self.assertEqual(self.nx.stopped, ['1'])
        self.nx.finished = True
        self.bridge.send('new.lua', b'new', slot=21)
        self.wait_for_idle()
        self.assertEqual(self.bridge.last['filename'], 'new.lua')
        self.assertEqual(self.nx.stopped, ['1'])

    def test_uses_available_adapter_instead_of_hci0(self):
        self.bridge.controller = None
        with mock.patch.object(self.bridge, 'start_agent') as agent:
            status = self.bridge.pair()
        self.assertEqual(self.nx.selected, '/org/bluez/hci1')
        self.assertEqual(status['adapter'], self.nx.selected)
        agent.assert_called_once()

    def test_unavailable_adapter_fails_before_pairing(self):
        self.bridge.controller = None
        self.bridge.adapter_path = '/org/bluez/hci9'
        with mock.patch.object(self.bridge, 'start_agent') as agent:
            with self.assertRaisesRegex(ValueError, 'unavailable'):
                self.bridge.pair()
        agent.assert_not_called()
        self.assertIsNone(self.nx.selected)

    def test_http_keeps_companion_api_and_rejects_non_object_body(self):
        token = 'test-only-token-1234567890'
        server = make_server(self.bridge, token, '127.0.0.1', 0)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        opener = build_opener(ProxyHandler({}))

        def request(endpoint, body=None, auth=True):
            headers = {'Content-Type': 'application/json'}
            if auth:
                headers['Authorization'] = 'Bearer ' + token
            req = Request(f'http://127.0.0.1:{server.server_port}{endpoint}',
                          None if body is None else json.dumps(body).encode(), headers)
            with opener.open(req, timeout=2) as response:
                return json.load(response)

        try:
            self.assertEqual(request('/status')['api_version'], 1)
            with self.assertRaises(HTTPError) as error:
                request('/status', auth=False)
            self.assertEqual(error.exception.code, 403)
            with self.assertRaises(HTTPError) as error:
                request('/send', [])
            self.assertEqual(error.exception.code, 400)
            self.assertEqual(self.nx.programs, [])
            request('/send', {'filename': 'hello.lua', 'source': base64.b64encode(b'print(1)').decode(), 'slot': 20})
            self.wait_for_idle()
            self.assertEqual(request('/status')['last']['state'], 'input sent')
        finally:
            server.shutdown()
            server.server_close()
            worker.join()


class BlueZOverrideTests(unittest.TestCase):
    def test_effective_unit_options_and_paths_are_preserved(self):
        unit = '[Service]\nExecStart=/old/bluetoothd\n[Service]\nExecStart=\nExecStart=/usr/libexec/bluetooth/bluetoothd --experimental --noplugin=sap\n'
        command = bluez_compat.input_only_command(unit)
        self.assertEqual(command, '/usr/libexec/bluetooth/bluetoothd --experimental --compat --noplugin=input,sap')
        self.assertNotIn('*', command)

    def test_foreign_wildcard_or_allowlist_is_rejected(self):
        for options in ('--noplugin=*', '--noplugin=in*', '--plugin=input,gatt', '--noplugin'):
            with self.subTest(options=options), self.assertRaises(ValueError):
                bluez_compat.input_only_command('[Service]\nExecStart=/usr/bin/bluetoothd ' + options)

    def test_enable_disable_changes_only_owned_override(self):
        with tempfile.TemporaryDirectory() as temp:
            override = Path(temp) / 'nxbt.conf'
            runner = mock.Mock(return_value='[Service]\nExecStart=/usr/lib/bluetooth/bluetoothd\n')
            bluez_compat.toggle_clean_bluez(True, override, runner)
            self.assertTrue(override.read_text().startswith(bluez_compat.MARKER))
            self.assertIn('--noplugin=input', override.read_text())
            count = runner.call_count
            bluez_compat.toggle_clean_bluez(True, override, runner)
            self.assertEqual(runner.call_count, count)
            bluez_compat.toggle_clean_bluez(False, override, runner)
            self.assertFalse(override.exists())
            override.write_text('# custom override\n')
            with self.assertRaises(ValueError):
                bluez_compat.toggle_clean_bluez(True, override, runner)
            bluez_compat.toggle_clean_bluez(False, override, runner)
            self.assertEqual(override.read_text(), '# custom override\n')

    def test_failed_restart_rolls_back_file_and_reloads(self):
        with tempfile.TemporaryDirectory() as temp:
            override = Path(temp) / 'nxbt.conf'
            calls = []

            def run(*args):
                calls.append(args)
                if args == ('cat', 'bluetooth.service'):
                    return '[Service]\nExecStart=/usr/sbin/bluetoothd\n'
                if args == ('restart', 'bluetooth.service') and calls.count(args) == 1:
                    raise subprocess.CalledProcessError(1, ['systemctl', *args])
                return ''

            with self.assertRaises(subprocess.CalledProcessError):
                bluez_compat.toggle_clean_bluez(True, override, run)
            self.assertFalse(override.exists())
            self.assertEqual(calls.count(('restart', 'bluetooth.service')), 2)


if __name__ == '__main__':
    unittest.main()
