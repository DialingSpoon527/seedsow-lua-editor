#!/usr/bin/env python3
"""Send a file to the editor receiver through a wired Pico or Pico W HTTP bridge."""

import argparse
import http.client
import json
import math
from pathlib import Path
import re
import sys
import time

from controller_protocol import BUTTONS, MAX_BYTES, destination, pack, symbols
from pico_uart import HATS, PicoUART


ALL_BUTTONS = [*BUTTONS, 'L', 'R']


class Controller:
    def __init__(self, config):
        self.host = config.get('host', '')
        self.port = config.get('port', 39391)
        self.token = config.get('token', '')
        if not isinstance(self.host, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.-]{0,252}', self.host):
            raise ValueError('Connection host must be an IPv4 address or hostname without http://.')
        if type(self.port) is not int or not 1 <= self.port <= 65535:
            raise ValueError('Connection port must be an integer from 1 to 65535.')
        if not isinstance(self.token, str) or (self.token and not re.fullmatch(r'[!-~]+', self.token)):
            raise ValueError('Connection token must contain printable ASCII without spaces.')
        self.held = set()

    def close(self):
        pass

    def request(self, endpoint, body=None):
        headers = {'Accept': 'application/json'}
        if self.token:
            headers['Authorization'] = 'Bearer ' + self.token
        payload = None
        if body is not None:
            headers['Content-Type'] = 'application/json'
            payload = json.dumps(body)
        connection = http.client.HTTPConnection(self.host, self.port, timeout=5)
        try:
            connection.request('GET' if body is None else 'POST', endpoint, payload, headers)
            with connection.getresponse() as response:
                if response.status in (401, 403):
                    raise ValueError('Controller rejected the token in your connection file.')
                if response.status == 404:
                    raise ValueError(f'Controller firmware does not provide {endpoint}.')
                if response.status != 200:
                    raise ValueError(f'Controller returned HTTP {response.status} for {endpoint}.')
                data = response.read(4097)
            if len(data) > 4096:
                raise ValueError('Controller response exceeded the size limit.')
            result = json.loads(data)
            if not isinstance(result, dict) or result.get('ok') is not True or result.get('confirmed') is False:
                raise ValueError(f'Controller did not confirm {endpoint}.')
            return result
        finally:
            connection.close()

    def clear(self):
        # Include every transport button even after a reply is lost.
        self.request('/release', {'buttons': ALL_BUTTONS})
        self.request('/release', {'buttons': list(HATS)})
        self.held.clear()

    def set_buttons(self, buttons):
        desired = set(buttons)
        released = sorted(self.held - desired)
        pressed = sorted(desired - self.held)
        if released:
            self.request('/release', {'buttons': released})
        if pressed:
            self.request('/press', {'buttons': pressed})
        self.held = desired


def calibrate(controller):
    time.sleep(2)
    for button in ALL_BUTTONS:
        controller.set_buttons([button])
        time.sleep(1.2)
        controller.set_buttons([])
        time.sleep(1)
    time.sleep(2)
    print('Calibration inputs sent. Confirm PC INPUT: 0 / ? bytes on the console.')


def transmit(controller, packet, prepare, hold):
    time.sleep(1)
    clock = False
    for index, nibble in enumerate(symbols(packet), 1):
        faces = [button for bit, button in enumerate(BUTTONS) if nibble & (1 << bit)]
        controller.set_buttons(faces + (['R'] if clock else []))
        time.sleep(prepare)
        clock = not clock
        controller.set_buttons(faces + (['R'] if clock else []))
        time.sleep(hold)
        if index % 128 == 0:
            print(f'Sent controller input for {index // 2}/{len(packet)} packet bytes.', flush=True)
    controller.set_buttons([])
    time.sleep(.5)
    print('Input sent. Confirm PC FILE SAVED, filename, byte count, and slot on the console.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    transport = parser.add_mutually_exclusive_group(required=True)
    transport.add_argument('--connection', type=Path, help='Private Pico W HTTP connection JSON')
    transport.add_argument('--serial-port', help='USB-to-UART adapter port for switch-pico firmware')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('status', help='Check the selected controller connection without pressing buttons')
    tap = sub.add_parser('tap', help='Test one button in the console button tester')
    tap.add_argument('button', choices=ALL_BUTTONS + list(HATS))
    tap.add_argument('--ready', action='store_true', help='Confirm the console is in its button tester')
    calibration = sub.add_parser('calibrate', help='Send A, B, X, Y, L, R to the calibration screen')
    calibration.add_argument('--ready', action='store_true', help='Confirm INPUT CALIBRATION is waiting for physical A')
    send = sub.add_parser('send', help='Send one file to a freshly armed editor receiver')
    send.add_argument('source', type=Path)
    send.add_argument('--slot', required=True, type=int, help='Unused uploader slot from 4 to 120')
    send.add_argument('--name', default='artemis-uploader.lua', help='New console filename')
    send.add_argument('--ready', action='store_true', help='Confirm receiver is at PC INPUT: 0 / ? bytes')
    send.add_argument('--prepare', type=float, default=.10)
    send.add_argument('--hold', type=float, default=.20)
    args = parser.parse_args(argv)
    controller = None
    packet = None
    changing = False
    code = 0
    try:
        if args.command != 'status' and not args.ready:
            raise ValueError('Check the console screen and add --ready before sending controller inputs.')
        if args.command == 'send':
            if not all(math.isfinite(n) and .10 <= n <= 2 for n in (args.prepare, args.hold)):
                raise ValueError('Both timing settings must be finite and between 0.10 and 2 seconds.')
            mode = destination(args.name, args.slot)
            with args.source.open('rb') as source:
                content = source.read(MAX_BYTES + 1)
            packet = pack(mode + '_' + args.name, content)
        if args.serial_port:
            controller = PicoUART(args.serial_port)
        else:
            config = json.loads(args.connection.read_text(encoding='utf-8-sig'))
            if not isinstance(config, dict):
                raise ValueError('Connection file must contain a JSON object.')
            controller = Controller(config)
        controller.request('/status')
        if args.command == 'status':
            if args.serial_port:
                print('UART adapter opened. Test a button to check that the Pico and console receive input.')
            else:
                print('Controller HTTP bridge answered. Test ordinary button input before calibration.')
        else:
            changing = True
            controller.clear()
            if args.command == 'tap':
                controller.set_buttons([args.button])
                time.sleep(.2)
                controller.set_buttons([])
                print('Tap sent. Confirm the button appeared in the console button tester.')
            elif args.command == 'calibrate':
                calibrate(controller)
            else:
                print(f'Sending {len(content)} source bytes to uploader slot {args.slot}.', flush=True)
                print(f'Allow at least {len(packet) * 2 * (args.prepare + args.hold) / 60:.1f} minutes plus network delays.', flush=True)
                transmit(controller, packet, args.prepare, args.hold)
    except KeyboardInterrupt:
        print('Stopped. Check the console receiver before starting a fresh attempt.', file=sys.stderr)
        code = 130
    except (OSError, ValueError, http.client.HTTPException, RecursionError) as error:
        print(f'Controller operation failed ({type(error).__name__}).', file=sys.stderr)
        if isinstance(error, ValueError) and not isinstance(error, json.JSONDecodeError):
            print(str(error), file=sys.stderr)
        print('No input was retried. Check the console before sending again.', file=sys.stderr)
        code = 1
    finally:
        if changing:
            try:
                time.sleep(.03)
                controller.clear()
            except (OSError, ValueError, http.client.HTTPException, KeyboardInterrupt, RecursionError):
                print('Button release could not be confirmed. Disconnect the controller before continuing.', file=sys.stderr)
                code = code or 1
        if controller:
            try:
                controller.close()
            except OSError:
                print('Controller connection could not close cleanly.', file=sys.stderr)
                code = code or 1
    return code


if __name__ == '__main__':
    raise SystemExit(main())
