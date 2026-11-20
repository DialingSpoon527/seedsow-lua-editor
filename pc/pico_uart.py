"""Host reports for the pinned switch-pico UART v3 firmware.

Wire-format reference: jyapayne/switch-pico at
02ff001ca206997229766256af0d0a096e26fb39, src/switch_pico_bridge/switch_pico_uart.py.
The firmware and upstream Python package are separate dependencies.
"""

import struct


BUTTON_BITS = {'Y': 0, 'B': 1, 'A': 2, 'X': 3, 'L': 4, 'R': 5}
HATS = {'DPAD_UP': 0, 'DPAD_RIGHT': 2, 'DPAD_DOWN': 4, 'DPAD_LEFT': 6}


def report(buttons):
    buttons = set(buttons)
    if buttons - BUTTON_BITS.keys() - HATS.keys():
        raise ValueError('Unsupported Pico button.')
    directions = buttons & HATS.keys()
    if len(directions) > 1:
        raise ValueError('Choose one D-pad direction.')
    mask = sum(1 << BUTTON_BITS[button] for button in buttons if button in BUTTON_BITS)
    hat = HATS[next(iter(directions))] if directions else 8
    payload = struct.pack('<HBBBBBB', mask, hat, 128, 128, 128, 128, 0)
    frame = bytes((0xAA, 3, len(payload), 0)) + payload
    return frame + bytes((sum(frame) & 255,))


class PicoUART:
    def __init__(self, port):
        try:
            import serial
        except ImportError as exc:
            raise ValueError('Install the serial dependency with: python -m pip install pyserial==3.5') from exc
        try:
            self.serial = serial.Serial(port, 921600, timeout=0, write_timeout=1)
        except serial.SerialException as exc:
            raise OSError('Could not open the UART adapter. Check its port and close other apps using it.') from exc

    def set_buttons(self, buttons):
        frame = report(buttons)
        try:
            count = self.serial.write(frame)
        except Exception as exc:
            raise OSError('UART write failed. Check the adapter and board connection.') from exc
        if count != len(frame):
            raise OSError('Incomplete UART report. Inspect the controller before sending again.')
        # Drain optional rumble replies without waiting for a response.
        self.serial.read(min(self.serial.in_waiting, 4096))

    def clear(self):
        self.set_buttons([])

    def request(self, endpoint):
        if endpoint != '/status':
            raise ValueError('Unsupported serial operation.')
        if not self.serial.is_open:
            raise OSError('UART adapter is closed.')
        return {'ok': True}

    def close(self):
        self.serial.close()
