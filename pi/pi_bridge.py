"""Authenticated LAN bridge to one Bluetooth controller; uploads remain data here."""
import argparse
import base64
import hmac
import json
import multiprocessing
import signal
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'pc'))
from controller_protocol import pack, macro, seconds, destination


class Bridge:
    def __init__(self, nx, controller_type, adapter_path=None):
        self.nx = nx
        self.controller_type = controller_type
        self.controller = None
        self.lock = threading.RLock()
        self.transfer = None
        self.last = None
        self.agent = None
        self.cancel = threading.Event()
        self.adapter_path = adapter_path

    def start_agent(self):
        if self.agent is not None and self.agent.poll() is None:
            return
        ready = threading.Event()
        agent = subprocess.Popen(
            [sys.executable, str(Path(__file__).with_name('pairing_agent.py'))],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

        def read_agent():
            with agent.stdout:
                for line in agent.stdout:
                    print('[pairing agent] ' + line.rstrip(), flush=True)
                    if line.startswith('Nintendo-only pairing agent ready'):
                        ready.set()

        threading.Thread(target=read_agent, daemon=True).start()
        if not ready.wait(5) or agent.poll() is not None:
            if agent.poll() is None:
                agent.terminate()
            try:
                agent.wait(timeout=3)
            except subprocess.TimeoutExpired:
                agent.kill()
                agent.wait(timeout=3)
            raise ValueError('Pairing agent could not register with BlueZ. Check the Pi service log.')
        self.agent = agent

    def status(self):
        with self.lock:
            state = {'state':'not paired'}
            if self.controller is not None:
                current = dict(self.nx.state.get(self.controller, {'state': 'initializing'}))
                state = {k:current.get(k) for k in ('state','errors','player_number')}
            return {'backend':'controller', 'controller':state,
                    'transfer':dict(self.transfer) if self.transfer is not None else None,
                    'last':dict(self.last) if self.last is not None else None,
                    'console_acknowledged':False, 'api_version':1,
                    'adapter':self.adapter_path}

    def pair(self, backend='controller', reset=False):
        if backend != 'controller':
            raise ValueError('This release uses the Bluetooth controller connection.')
        with self.lock:
            if self.transfer:
                raise ValueError('Stop transmission before pairing again.')
            current = self.nx.state.get(self.controller, {})
            if self.controller is not None and (reset or current.get('state')=='crashed'):
                previous = self.controller
                self.nx.remove_controller(previous)
                self.controller = None
                deadline = time.monotonic()+5
                while previous in self.nx.state:
                    if time.monotonic() > deadline:
                        raise ValueError('Previous controller is still closing; try Pair again.')
                    time.sleep(.02)
                time.sleep(.15)
            if self.controller is None:
                adapters = sorted(str(path) for path in self.nx.get_available_adapters())
                if not adapters:
                    raise ValueError('No Bluetooth adapters are available. Check power, rfkill, and other controller processes.')
                selected = self.adapter_path or adapters[0]
                if selected not in adapters:
                    raise ValueError('The configured Bluetooth adapter is unavailable. Check the adapter setting and Pi service log.')
                self.start_agent()
                self.controller = self.nx.create_controller(self.controller_type, adapter_path=selected)
                self.adapter_path = selected
        return self.status()

    def connected(self):
        if self.controller is None or self.nx.state.get(self.controller, {}).get('state') != 'connected':
            raise ValueError('Pair the Pi in Controllers → Change Grip/Order first.')

    def _start(self, program, job, timeout):
        with self.lock:
            self.connected()
            if self.transfer:
                raise ValueError('A transmission is already active.')
            cancel = threading.Event()
            self.cancel = cancel
            controller = self.controller
            mid = self.nx.macro(controller, program, block=False)
            job['macro_id'] = mid
            self.transfer = job

        def worker():
            try:
                deadline = time.monotonic()+timeout
                while True:
                    if cancel.wait(.05):
                        raise ValueError('Transmission stopped.')
                    current = self.nx.state.get(controller, {})
                    if current.get('state') != 'connected':
                        raise ValueError('Controller disconnected.')
                    if mid in current.get('finished_macros', []):
                        break
                    if time.monotonic() > deadline:
                        raise ValueError('Controller transmission timed out.')
                if cancel.is_set():
                    raise ValueError('Transmission stopped.')
                result = {'state':job['success_state'], 'filename':job['filename'], 'bytes':job['bytes'],
                          'note':job['success_note']}
            except Exception as error:
                result = {'state':'failed', 'error':str(error)}
                try:
                    with self.lock:
                        if not job.get('stop_queued'):
                            self.nx.stop_macro(controller, mid, block=False)
                            job['stop_queued'] = True
                except Exception:
                    with self.lock:
                        job['state'] = 'stop unconfirmed'
                        self.last = result
                    return
            with self.lock:
                if self.transfer is job:
                    self.last = result
                    self.transfer = None

        threading.Thread(target=worker, daemon=True).start()
        return self.status()

    def send(self, name, source, prepare=.05, hold=.10, slot=None):
        mode = destination(name, slot)
        packet = pack(mode+'_'+name, source)
        program = macro(packet, prepare, hold)
        estimate = seconds(packet, prepare, hold)
        return self._start(program, {'filename':name, 'bytes':len(source), 'started':time.time(),
                    'estimated_seconds':estimate, 'state':'sending', 'backend':'controller',
                    'success_state':'input sent',
                    'success_note':'Check PC FILE SAVED on the console. Input sent is not console confirmation.'},
                    estimate*1.5+60)

    def calibration(self):
        program = '2.0s\n'+''.join(b+' 1.2s\n1.0s\n' for b in ('A','B','X','Y','L','R'))+'2.0s\n'
        return self._start(program, {'filename':'Input calibration', 'bytes':0, 'started':time.time(),
                    'estimated_seconds':18, 'state':'calibrating', 'backend':'controller',
                    'success_state':'calibration inputs sent',
                    'success_note':'Check that the console shows PC INPUT: 0 / ? bytes.'}, 45)

    def tap(self, button, down=.12, up=.16):
        if button not in ('A','B','X','Y','L','R','ZL','ZR','PLUS','MINUS',
                          'DPAD_UP','DPAD_DOWN','DPAD_LEFT','DPAD_RIGHT'):
            raise ValueError('Unsupported button.')
        if not .05 <= down <= 2 or not .08 <= up <= 2:
            raise ValueError('Button timing outside supported limits.')
        with self.lock:
            self.connected()
            if self.transfer:
                raise ValueError('Manual buttons are disabled during transmission.')
            self.nx.press_buttons(self.controller, [button], down=down, up=up, block=False)

    def stop(self):
        with self.lock:
            self.cancel.set()
            if self.transfer:
                self.transfer['state'] = 'stopping'
                if self.transfer.get('macro_id') is not None and not self.transfer.get('stop_queued'):
                    self.nx.stop_macro(self.controller, self.transfer['macro_id'], block=False)
                    self.transfer['stop_queued'] = True
                return
            if self.controller is not None:
                self.nx.clear_macros(self.controller)
            self.last = {'state':'stopped', 'note':'Hold L on the console to cancel its receiver.'}


def make_server(bridge, token, host, port):
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(15)

        def log_message(self, *args):
            pass

        def reply(self, status, value):
            data = json.dumps(value).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def authorized(self):
            actual = self.headers.get('Authorization', '').encode('utf-8')
            return hmac.compare_digest(actual, ('Bearer '+token).encode('utf-8'))

        def do_GET(self):
            if not self.authorized():
                return self.reply(403, {'error':'Connection token required.'})
            if self.path != '/status':
                return self.reply(404, {'error':'Unknown path.'})
            try:
                self.reply(200, bridge.status())
            except Exception as error:
                self.reply(500, {'error':str(error)})

        def do_POST(self):
            if not self.authorized():
                return self.reply(403, {'error':'Connection token required.'})
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 <= size <= 1500000:
                    raise ValueError('Request too large.')
                data = json.loads(self.rfile.read(size) or b'{}')
                if not isinstance(data, dict):
                    raise ValueError('Request body must contain a JSON object.')
                if self.path == '/pair':
                    result = bridge.pair(data.get('backend','controller'), data.get('reset',True) is True)
                elif self.path == '/send':
                    if data.get('backend','controller') != 'controller':
                        raise ValueError('Choose Controller.')
                    result = bridge.send(data['filename'], base64.b64decode(data['source'], validate=True),
                                         float(data.get('prepare',.05)), float(data.get('hold',.10)), data.get('slot'))
                elif self.path == '/tap':
                    bridge.tap(data['button'], float(data.get('down',.12)), float(data.get('up',.16)))
                    result = {'queued':True}
                elif self.path == '/calibrate':
                    result = bridge.calibration()
                elif self.path == '/stop':
                    bridge.stop()
                    result = bridge.status()
                else:
                    return self.reply(404, {'error':'Unknown path.'})
                self.reply(200, result)
            except (ValueError, KeyError, TypeError) as error:
                self.reply(400, {'error':str(error)})
            except Exception as error:
                self.reply(500, {'error':str(error)})

    return ThreadingHTTPServer((host, port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    config = json.loads(parser.parse_args().config.read_text())
    if not isinstance(config.get('token'), str) or len(config['token']) < 32:
        parser.error('The bridge needs a connection token of at least 32 characters.')
    # NXBT's bound process targets rely on Linux fork semantics. Set this before
    # the dependency creates any workers or this service starts any threads.
    if multiprocessing.get_start_method(allow_none=True) is None:
        multiprocessing.set_start_method('fork')
    elif multiprocessing.get_start_method() != 'fork':
        parser.error('This pinned NXBT backend requires the Linux fork start method.')
    sys.path.insert(0, config.get('nxbt_path', str(Path(__file__).resolve().parents[1]/'vendor')))
    subprocess.run(['rfkill','unblock','bluetooth'], check=True)
    import nxbt
    import dbus.mainloop.glib
    from gi.repository import GLib
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    nx = nxbt.Nxbt()
    bridge = Bridge(nx, nxbt.PRO_CONTROLLER, config.get('adapter'))
    loop = GLib.MainLoop()
    threading.Thread(target=loop.run, daemon=True).start()
    server = make_server(bridge, config['token'], config.get('bind','0.0.0.0'), config.get('port',39391))
    print('Seedsow controller bridge ready on port '+str(server.server_port), flush=True)
    signal.signal(signal.SIGTERM, lambda *_:threading.Thread(target=server.shutdown, daemon=True).start())
    try:
        server.serve_forever()
    finally:
        server.server_close()
        bridge.stop()
        if bridge.agent and bridge.agent.poll() is None:
            bridge.agent.terminate()
        if bridge.controller is not None:
            nx.remove_controller(bridge.controller)
        nx._on_exit()
        loop.quit()


if __name__ == '__main__':
    main()
