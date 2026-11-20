"""Apply focused compatibility fixes to the pinned NXBT dependency."""
import argparse
from pathlib import Path
import re


def replace_once(text, before, after, label):
    if text.count(after) == 1:
        return text
    if text.count(before) != 1:
        raise ValueError('Unexpected pinned NXBT source for ' + label)
    return text.replace(before, after)


def patch(root):
    root = Path(root)
    paths = ['nxbt.py', 'bluez.py', 'controller/server.py', 'controller/controller.py']
    changed = {name: (root / name).read_text() for name in paths}

    text = changed['nxbt.py']
    start = text.index('    def get_available_adapters(self):')
    end = text.index('    def get_switch_addresses(self):', start)
    section = replace_once(text[start:end], 'bus = dbus.SystemBus()',
                           'bus = dbus.SystemBus(private=True)\n        bus.set_exit_on_disconnect(False)', 'private adapter bus')
    changed['nxbt.py'] = text[:start] + section + text[end:]

    text = changed['bluez.py'].replace('        bus = dbus.SystemBus()',
                                      '        bus = dbus.SystemBus(private=True)\n        bus.set_exit_on_disconnect(False)')
    start = text.index('def toggle_clean_bluez(toggle):')
    end = text.index('def clean_sdp_records():', start)
    text = text[:start] + (
        'def toggle_clean_bluez(toggle):\n'
        '    from .seedsow_bluez import toggle_clean_bluez as apply_override\n'
        '    apply_override(toggle)\n\n\n'
    ) + text[end:]
    changed['bluez.py'] = text

    text = changed['controller/server.py']
    text = replace_once(text, 'if msg[3:] != self.cached_msg:',
                        "if self.protocol.mode == 'standard' or msg[3:] != self.cached_msg:", 'continuous reports')
    if 'self.state["player_number"] = self.protocol.player_number' not in text:
        text, count = re.subn(r'^( +)self.protocol.process_commands\(reply\)$',
                             r'\1self.protocol.process_commands(reply)\n\1self.state["player_number"] = self.protocol.player_number',
                             text, flags=re.M)
        if not count:
            raise ValueError('Unexpected pinned NXBT protocol loop')
    start = text.index('    def mainloop(')
    end = text.index('    def save_connection(', start)
    loop = replace_once(text[start:end],
                        '            except BlockingIOError:\n                reply = None',
                        '            except BlockingIOError:\n                reply = None\n'
                        '            except OSError as error:\n'
                        '                itr, ctrl = self.save_connection(error)\n'
                        '                continue', 'socket reset recovery')
    text = text[:start] + loop + text[end:]
    text = replace_once(text, 'self.switch_address = itr.getsockname()[0]',
                        'self.switch_address = itr.getpeername()[0]', 'remote reconnect address')
    changed['controller/server.py'] = text

    text = changed['controller/controller.py']
    text = replace_once(text, 'self.bt.set_discoverable_timeout(180)',
                        'self.bt.set_discoverable_timeout(0)', 'pairing discoverability')
    text = replace_once(text,
                        '        except dbus.exceptions.DBusException as e:\n            self.logger.debug(e)',
                        '        except dbus.exceptions.DBusException as e:\n'
                        '            if e.get_dbus_name() != "org.bluez.Error.AlreadyExists":\n'
                        '                raise\n'
                        '            self.logger.warning("Controller profile already registered")',
                        'profile registration error reporting')
    changed['controller/controller.py'] = text
    changed['seedsow_bluez.py'] = Path(__file__).with_name('bluez_compat.py').read_text()
    for name, text in changed.items():
        compile(text, name, 'exec')
    for name, text in changed.items():
        (root / name).write_text(text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('nxbt_package', type=Path)
    patch(parser.parse_args().nxbt_package)
