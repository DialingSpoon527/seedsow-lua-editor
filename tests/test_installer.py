"""Offline checks: no console or native exploit is executed by these tests."""
import hashlib
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import re
import queue
import socket
import struct
import tempfile
import threading
import unittest
from unittest import mock
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


sheet = module('sheet', 'tools/make_sheet.py')
sender = module('sender', 'pc/send_alula.py')

try:
    from lupa.lua51 import LuaRuntime
except ImportError:
    LuaRuntime = None


class GeneratedSource(unittest.TestCase):
    def test_exact_body_and_keyboard_reconstruction(self):
        body = (ROOT / 'uploader/r14_body.lua').read_bytes()
        self.assertEqual(len(body), 3599)
        self.assertEqual(hashlib.sha256(body).hexdigest(), sheet.BODY_SHA256)
        for ip, port, slot, uploader in [('10.0.0.2', 1024, 4, 120), ('192.168.100.100', 65535, 120, 119)]:
            with self.subTest(settings=(ip, port, slot, uploader)), tempfile.TemporaryDirectory() as temp:
                config, out = sheet.generate(ip, port, slot, uploader, temp)
                source = (out / 'TYPE_THIS_EXACT.lua').read_bytes()
                chunks = (out / 'ONE_ENTRY_PER_LINE.txt').read_text('ascii').splitlines()
                self.assertEqual(''.join(chunks).encode('ascii'), source)
                self.assertEqual(source, f'local PC_IP="{ip}";local TARGET_SLOT={slot};local PC_PORT={port};'.encode() + body)
                self.assertTrue(all(0 < len(chunk) <= 32 and chunk == chunk.strip() for chunk in chunks))
                self.assertEqual(config['source_sha256'], hashlib.sha256(source).hexdigest())
                self.assertEqual(config, json.loads((out / 'config.json').read_text()))
                # Escape sequences must stay together across system keyboard entries.
                boundaries = set()
                offset = 0
                for chunk in chunks[3:]:
                    offset += len(chunk)
                    boundaries.add(offset)
                for escape in re.finditer(r'\\(?:[0-9]{1,3}|.)', body.decode('ascii')):
                    self.assertFalse(any(escape.start() < n < escape.end() for n in boundaries))
                if LuaRuntime:
                    # Compile without running the native body.
                    lua = LuaRuntime()
                    self.assertIsNotNone(lua.eval('function(s) return assert(loadstring(s)) end')(source.decode()))

    def test_invalid_configuration_is_rejected(self):
        for args in [('127.0.0.1', 1024, 4, 5), ('0.0.0.0', 1024, 4, 5),
                     ('8.8.8.8', 1024, 4, 5), ('169.254.0.2', 1024, 4, 5),
                     ('10.0.0.2', 0, 4, 5), ('10.0.0.2', 65536, 4, 5),
                     ('10.0.0.2', 1024, 3, 5), ('10.0.0.2', 1024, 4, 4),
                     ('10.0.0.2', 1024, 4, 121)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                sheet.validate(*args)

    def test_modified_native_body_is_rejected(self):
        original = Path.read_bytes

        def damaged(path):
            value = original(path)
            return value + b' ' if path.name == 'r14_body.lua' else value

        with tempfile.TemporaryDirectory() as temp, mock.patch.object(Path, 'read_bytes', damaged):
            with self.assertRaisesRegex(ValueError, 'body has changed'):
                sheet.generate('10.0.0.2', 1024, 4, 5, temp)
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_preparation_keeps_typing_configuration(self):
        with tempfile.TemporaryDirectory() as temp:
            _, out = sheet.generate('10.0.0.2', 1024, 4, 5, temp)
            before = (out / 'config.json').read_bytes()
            sender.write_build([('example', b'abc')], b'installer', out, '1234abcd')
            self.assertEqual((out / 'config.json').read_bytes(), before)
            self.assertTrue((out / 'sender-manifest.json').is_file())

    def test_unexpected_release_archive_is_rejected_before_parsing(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'wrong.zip'
            path.write_bytes(b'wrong download')
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                sender.load_release(path)

    def test_documentation_links_resolve(self):
        for path in [ROOT / 'README.md', ROOT / 'THIRD_PARTY_NOTICES.md', *sorted((ROOT / 'docs').glob('*.md'))]:
            for link in re.findall(r'\]\(([^)]+)\)', path.read_text('utf-8')):
                target = unquote(link.split('#')[0])
                if target and not urlsplit(target).scheme:
                    with self.subTest(document=path.name, target=target):
                        self.assertTrue((path.parent / target).is_file(), target)


class TcpSender(unittest.TestCase):
    def test_exact_packets_with_fragmented_client_reads(self):
        # Listen on an OS-selected loopback port and read in deliberately small
        # pieces, independently reconstructing the length-prefixed wire stream.
        endpoint = queue.Queue()
        errors = queue.Queue()
        original_socket = socket.socket

        class ListeningSocket(original_socket):
            def listen(self, backlog):
                super().listen(backlog)
                endpoint.put(self.getsockname())

        stage = b'installer\0stage'
        files = [('binary', bytes(range(256)) * 40), ('last', b'last\0file')]

        def server():
            try:
                sender.serve(stage, files, '127.0.0.1', 0)
            except Exception as error:
                errors.put(error)
                endpoint.put(None)

        with contextlib.redirect_stdout(io.StringIO()), mock.patch.object(sender.socket, 'socket', ListeningSocket):
            thread = threading.Thread(target=server, daemon=True)
            thread.start()
            address = endpoint.get(timeout=3)
            self.assertIsNotNone(address)
            with original_socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.settimeout(3)
                client.connect(address)
                wire = bytearray()
                while True:
                    piece = client.recv(7)
                    if not piece:
                        break
                    wire.extend(piece)
            thread.join(timeout=3)
        self.assertFalse(thread.is_alive())
        if not errors.empty():
            raise errors.get()
        offset = 0
        for expected in [stage, *(data for _, data in files)]:
            length, = struct.unpack_from('<I', wire, offset)
            offset += 4
            self.assertEqual(length, len(expected))
            self.assertEqual(wire[offset:offset + length], expected)
            offset += length
        self.assertEqual(offset, len(wire))


@unittest.skipUnless(LuaRuntime, 'Install requirements-dev.txt for Lua 5.1 installer simulations')
class StreamedInstaller(unittest.TestCase):
    def run_install(self, *, occupied=False, collision=False, corrupt=False, interrupted_write=False):
        lua = LuaRuntime(encoding=None, unpack_returned_tuples=True)
        files = [('ax_core.lua', b'core\0bytes'), ('ax_http.lua', b'http'), ('__SIDECAR__', b'sidecar')]
        initial = {b'ss030.asb': b'bootstrap', b'ssseed030.bin': b'seed', b'ssethumb.png': b'thumb',
                   b'saveg.dat': b'global metadata', b'ssedit1.lua': b'recovery',
                   b'ssslot020.ref': b'user.lua\n', b'user.lua': b'keep me'}
        if occupied:
            initial[b'save0030.dat'] = b'old save'
        if collision:
            initial[b'ax_core.lua'] = b'other core'
        store = dict(initial)
        writes = []
        packet = b''.join(struct.pack('<I', len(data)) + data for _, data in files)
        if corrupt:
            packet = packet.replace(b'core\0bytes', b'cOre\0bytes')
        position = 0

        def rx(count):
            nonlocal position
            data = packet[position:position + count]
            position += count
            return data

        def write(name, data):
            writes.append(name)
            if interrupted_write and name == b'ax_http.lua':
                return False
            store[name] = data
            return True

        editor = lua.table_from({b'read': lambda name: store.get(name), b'write': write})
        engine = lua.table_from({b'isFileExists': lambda _, path: path.removeprefix(b'save:/') in store})
        stage = sender.stage_lua(files, '1234abcd').encode('ascii')
        lua.execute(stage, rx, editor, 30, engine)
        return initial, store, writes

    def test_success_preserves_existing_files_and_commits_reference_last(self):
        initial, files, writes = self.run_install()
        for name, data in initial.items():
            self.assertEqual(files[name], data)
        self.assertEqual(writes[-2:], [b'ssslot030.ref', b'ax_install.log'])
        self.assertEqual(files[b'ssslot030.ref'], b'ax_slot030.lua\n')
        self.assertIn(b'R14_COMPLETE SLOT=30 RUN=1234abcd', files[b'ax_install.log'])
        self.assertEqual(files[b'ax_core.lua'], b'core\0bytes')

    def test_preflight_failures_write_only_the_failure_log(self):
        for option, error in [('occupied', b'SLOT_IN_USE'), ('collision', b'COLLISION'), ('corrupt', b'Damaged file')]:
            with self.subTest(option=option):
                initial, files, writes = self.run_install(**{option: True})
                self.assertEqual(writes, [b'ax_install.log'])
                self.assertIn(error, files[b'ax_install.log'])
                self.assertIn(b'R14_FAILED', files[b'ax_install.log'])
                self.assertNotIn(b'R14_COMPLETE', files[b'ax_install.log'])
                self.assertEqual({k: v for k, v in files.items() if k != b'ax_install.log'}, initial)

    def test_interrupted_write_never_publishes_a_slot(self):
        _, files, _ = self.run_install(interrupted_write=True)
        self.assertNotIn(b'ssslot030.ref', files)
        self.assertIn(b'R14_FAILED', files[b'ax_install.log'])
        self.assertNotIn(b'R14_COMPLETE', files[b'ax_install.log'])


if __name__ == '__main__':
    unittest.main()
