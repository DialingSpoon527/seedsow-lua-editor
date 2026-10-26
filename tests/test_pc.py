"""PC-to-bridge integration, binary preservation and private configuration checks."""
import base64
import json
import sys
import tempfile
import threading
import time
import unittest
import zipfile
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT/n) for n in ('pc','pi','editor')]
from client import BridgeClient, load_settings, save_settings, upload_request, validate_connection
from pi_bridge import Bridge, make_server
from protocol import unpack, destination
from build import load_backup


class FakeNX:
    def __init__(self):
        self.state = {0:{'state':'connected','player_number':1,'errors':False,'finished_macros':[]}}
        self.programs = []
        self.buttons = []
    def macro(self,index,program,block=False):
        self.programs.append(program)
        self.state[index]['finished_macros'].append(str(len(self.programs)))
        return str(len(self.programs))
    def press_buttons(self,index,buttons,**kwargs):
        self.buttons.extend(buttons)
    def clear_macros(self,index):
        pass


class PCIntegration(unittest.TestCase):
    def setUp(self):
        self.nx = FakeNX()
        self.bridge = Bridge(self.nx,None)
        self.bridge.controller = 0
        self.token = 'test-only-connection-token-1234567890'
        self.server = make_server(self.bridge,self.token,'127.0.0.1',0)
        self.thread = threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.config = {'host':'127.0.0.1','port':self.server.server_port,'token':self.token}
        self.client = BridgeClient(self.config)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def wait(self):
        deadline = time.monotonic()+3
        while self.bridge.transfer and time.monotonic()<deadline:
            time.sleep(.01)
        self.assertIsNone(self.bridge.transfer)

    def test_file_request_reaches_real_macro_and_preserves_binary(self):
        source = bytes(range(256))
        body,eta = upload_request('sample.bin',source,None)
        self.assertEqual(base64.b64decode(body['source']),source)
        self.assertGreater(eta,0)
        self.client.request('/send',body)
        self.wait()
        program = self.nx.programs[0]
        # Decode each actual generated clock-edge symbol, independently of the packer.
        values = []
        for line in program.splitlines()[2:-1:2]:
            buttons = line.split()[:-1]
            values.append(sum(1<<bit for bit,name in enumerate(('A','B','X','Y')) if name in buttons))
        packet = bytes((values[i]<<4)|values[i+1] for i in range(0,len(values),2))
        self.assertEqual(unpack(packet),('F000_sample.bin',source))
        self.assertEqual(self.bridge.last['state'],'input sent')
        self.assertFalse(self.client.request('/status')['console_acknowledged'])

    def test_authentication_and_manual_button_validation(self):
        with self.assertRaises(HTTPError) as error:
            urlopen(f'http://127.0.0.1:{self.server.server_port}/status')
        self.assertEqual(error.exception.code,403)
        wrong = BridgeClient(dict(self.config,token='wrong-token-for-local-test'))
        with self.assertRaisesRegex(RuntimeError,'token was rejected'):
            wrong.request('/status')
        with self.assertRaisesRegex(RuntimeError,'Unsupported button'):
            self.client.request('/tap',{'button':'HOME'})
        self.client.request('/tap',{'button':'L','down':1,'up':.3})
        self.assertEqual(self.nx.buttons,['L'])

    def test_calibration_and_disconnected_requests(self):
        self.client.request('/calibrate',{})
        self.wait()
        self.assertIn('R 1.2s',self.nx.programs[0])
        self.assertEqual(self.bridge.last['state'],'calibration inputs sent')
        self.nx.state[0]['state'] = 'disconnected'
        body,_ = upload_request('hello.lua',b'print(1)',20)
        with self.assertRaisesRegex(RuntimeError,'Pair the Pi'):
            self.client.request('/send',body)

    def test_destinations_fail_before_transmission(self):
        for filename,slot in [('ssedit1.lua',20),('../file.lua',20),('file.lua',1),('file.lua',True),('save0002.dat',None)]:
            with self.subTest(filename=filename,slot=slot):
                with self.assertRaises(ValueError):
                    upload_request(filename,b'test',slot)
        self.assertEqual(destination('hello.lua',6),'P006')
        with self.assertRaises(ValueError):
            upload_request('big.bin',b'x'*1048577,None)


class PrivateSettings(unittest.TestCase):
    def test_settings_ignore_unrelated_fields(self):
        config = {'host':'raspberrypi.local','port':39391,'token':'test-only-private-token-1234','extra':'discard me'}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'settings.json'
            self.assertEqual(load_settings(path),{})
            save_settings(config,path)
            self.assertNotIn('extra',load_settings(path))
            self.assertFalse(path.with_suffix('.tmp').exists())
        for host in ('http://pi','pi:39391','pi/path','pi\nheader'):
            with self.assertRaises(ValueError):
                validate_connection(dict(config,host=host))

    def test_backup_rejects_traversal_and_duplicate_names(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'bad.zip'
            with zipfile.ZipFile(path,'w') as archive:
                archive.writestr('../saveg.dat',b'test')
            with self.assertRaisesRegex(ValueError,'unsafe filename'):
                load_backup(path)
            with zipfile.ZipFile(path,'w') as archive:
                archive.writestr('one/saveg.dat',b'test')
                archive.writestr('two/saveg.dat',b'test')
            with self.assertRaisesRegex(ValueError,'collection of backups'):
                load_backup(path)


if __name__ == '__main__':
    unittest.main()
