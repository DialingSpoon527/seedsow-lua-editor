"""Apply the three controller fixes used by the original V3 hardware trial."""
import argparse
import re
from pathlib import Path

def patch(root):
    root = Path(root)
    path = root/'nxbt.py'
    text = path.read_text()
    start = text.index('    def get_available_adapters(self):')
    end = text.index('    def get_switch_addresses(self):', start)
    section = text[start:end]
    if 'dbus.SystemBus(private=True)' not in section:
        if section.count('bus = dbus.SystemBus()') != 1:
            raise ValueError('Unexpected NXBT adapter code.')
        section = section.replace('bus = dbus.SystemBus()',
                                  'bus = dbus.SystemBus(private=True)\n        bus.set_exit_on_disconnect(False)')
    path.write_text(text[:start]+section+text[end:])
    path = root/'bluez.py'
    text = path.read_text()
    text = text.replace('        bus = dbus.SystemBus()',
                        '        bus = dbus.SystemBus(private=True)\n        bus.set_exit_on_disconnect(False)')
    path.write_text(text)
    path = root/'controller/server.py'
    text = path.read_text()
    before = 'if msg[3:] != self.cached_msg:'
    after = "if self.protocol.mode == 'standard' or msg[3:] != self.cached_msg:"
    if before in text:
        if text.count(before) != 1:
            raise ValueError('Unexpected NXBT report loop.')
        text = text.replace(before, after)
    elif after not in text:
        raise ValueError('NXBT report loop is missing.')
    if 'self.state["player_number"] = self.protocol.player_number' not in text:
        text, count = re.subn(r'^( +)self.protocol.process_commands\(reply\)$',
                             r'\1self.protocol.process_commands(reply)\n\1self.state["player_number"] = self.protocol.player_number',
                             text, flags=re.M)
        if not count:
            raise ValueError('Unexpected NXBT protocol loop.')
    path.write_text(text)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('nxbt_package', type=Path)
    patch(p.parse_args().nxbt_package)
