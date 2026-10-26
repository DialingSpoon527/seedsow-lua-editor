"""PC settings, upload validation and the bridge HTTP client (standard library only)."""
import base64
import json
import os
import socket
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, ProxyHandler

from protocol import destination, pack, seconds

SPEEDS = {'Normal':(.05,.10), 'Slow':(.10,.20), 'Fast':(.03,.06)}


def settings_path():
    override = os.environ.get('SEEDSOW_SETTINGS')
    if override:
        return Path(override).expanduser()
    return Path(os.environ.get('LOCALAPPDATA', Path.home()/'.config'))/'SeedsowLuaEditor/settings.json'


def validate_connection(config):
    host = str(config.get('host','')).strip()
    if not host or any(c in host for c in '/\\:@?# \t\r\n'):
        raise ValueError('Enter the Pi hostname or IPv4 address, without http:// or a port.')
    port = int(config.get('port',39391))
    if not 1 <= port <= 65535:
        raise ValueError('Port must be between 1 and 65535.')
    token = config.get('token','')
    if not isinstance(token,str) or len(token) < 16 or any(ord(c)<33 or ord(c)>126 for c in token):
        raise ValueError('Import the private connection file exported by your Pi, or enter its token.')
    return {'host':host, 'port':port, 'token':token}


def load_settings(path=None):
    path = Path(path) if path else settings_path()
    if not path.exists():
        return {}
    config = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(config,dict):
        raise ValueError('Settings file must contain a JSON object.')
    return config


def save_settings(config, path=None):
    config = validate_connection(config)
    path = Path(path) if path else settings_path()
    path.parent.mkdir(parents=True,exist_ok=True)
    staging = path.with_suffix('.tmp')
    with open(staging,'w',encoding='utf-8',opener=lambda n,f:os.open(n,f,0o600)) as file:
        json.dump(config,file,indent=2)
        file.write('\n')
    staging.replace(path)
    return config


def upload_request(filename, source, slot=20, speed='Normal'):
    mode = destination(filename,slot)
    if not isinstance(source,bytes):
        raise ValueError('File contents must be bytes.')
    prepare,hold = SPEEDS[speed]
    packet = pack(mode+'_'+filename,source)
    return {'filename':filename, 'source':base64.b64encode(source).decode('ascii'),
            'slot':slot, 'backend':'controller', 'prepare':prepare, 'hold':hold}, seconds(packet,prepare,hold)


class BridgeClient:
    def __init__(self,config,timeout=5):
        self.config = validate_connection(config)
        self.timeout = timeout
        self.opener = build_opener(ProxyHandler({}))  # The Pi is a direct LAN connection.

    def request(self,path,data=None):
        config = self.config
        address = f"http://{config['host']}:{config['port']}{path}"
        body = None if data is None else json.dumps(data).encode('utf-8')
        request = Request(address,data=body,headers={
            'Authorization':'Bearer '+config['token'], 'Content-Type':'application/json'})
        try:
            with self.opener.open(request,timeout=self.timeout) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code == 403:
                raise RuntimeError('Connection token was rejected. Import the Pi connection file again.') from None
            try:
                message = json.loads(error.read()).get('error','Bridge request failed.')
            except (ValueError,AttributeError):
                message = f'Bridge returned HTTP {error.code}.'
            raise RuntimeError(message) from None
        except (URLError,TimeoutError,socket.timeout):
            raise RuntimeError('Cannot reach the Pi. Check its address, power, network and bridge service.') from None
