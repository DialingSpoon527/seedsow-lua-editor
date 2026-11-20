"""Manage only our temporary BlueZ Input-plugin override.

Installed into the pinned NXBT package by patch_nxbt.py. Importing this module
does not change Bluetooth configuration. The bridge constructor enables the
override and its shutdown removes it, as in the original companion.
"""

import logging
from pathlib import Path
import shlex
import subprocess


OVERRIDE = Path('/run/systemd/system/bluetooth.service.d/nxbt.conf')
MARKER = '# Seedsow input-only Bluetooth override\n'


def run_systemctl(*args):
    return subprocess.run(['systemctl', *args], check=True, capture_output=True,
                          text=True, timeout=25).stdout


def input_only_command(unit_text):
    """Read effective ExecStart directives in systemctl cat output."""
    commands = []
    section = ''
    pending = ''
    for raw in unit_text.splitlines():
        line = pending + raw.strip()
        if line.endswith('\\'):
            pending = line[:-1] + ' '
            continue
        pending = ''
        if not line or line.startswith(('#', ';')):
            continue
        if line.startswith('['):
            section = line
        elif section == '[Service]' and line.startswith('ExecStart='):
            value = line.partition('=')[2].strip()
            if value:
                commands.append(value)
            else:
                commands.clear()
    if pending or len(commands) != 1:
        raise ValueError('Cannot identify one Bluetooth ExecStart command. Review bluetooth.service overrides.')
    args = shlex.split(commands[0])
    if not args or 'bluetoothd' != Path(args[0]).name:
        raise ValueError('Bluetooth service does not run bluetoothd directly. Review its ExecStart command.')
    kept = [args[0]]
    disabled = []
    index = 1
    while index < len(args):
        arg = args[index]
        if arg == '--noplugin':
            index += 1
            if index == len(args):
                raise ValueError('Bluetooth service has an incomplete --noplugin option.')
            disabled.extend(args[index].split(','))
        elif arg.startswith('--noplugin='):
            disabled.extend(arg.partition('=')[2].split(','))
        elif arg in ('--plugin', '-p') or arg.startswith('--plugin='):
            raise ValueError('Bluetooth service uses a plugin allowlist. Review it before enabling the controller.')
        else:
            kept.append(arg)
        index += 1
    if any('*' in name or '?' in name or '[' in name for name in disabled):
        raise ValueError('An existing Bluetooth override disables plugins by wildcard. Stop the old bridge and review that override first.')
    if '--compat' not in kept and '-C' not in kept:
        kept.append('--compat')
    kept.append('--noplugin=' + ','.join(sorted(set(disabled) | {'input'})))
    return shlex.join(kept)


def toggle_clean_bluez(enable, override=OVERRIDE, run=run_systemctl):
    previous = override.read_text() if override.exists() else None
    owned = previous is not None and previous.startswith(MARKER)
    if enable and owned:
        return
    if previous is not None and not owned:
        if enable:
            raise ValueError('An older or custom nxbt.conf exists. Stop the old bridge and inspect it before restarting.')
        return
    if not enable and not owned:
        return

    if enable:
        command = input_only_command(run('cat', 'bluetooth.service'))
        override.parent.mkdir(parents=True, exist_ok=True)
        content = MARKER + '[Service]\nExecStart=\nExecStart=' + command + '\n'
        override.write_text(content)
    else:
        override.unlink()
    try:
        run('daemon-reload')
        run('restart', 'bluetooth.service')
    except (OSError, subprocess.SubprocessError):
        if previous is None:
            override.unlink(missing_ok=True)
        else:
            override.write_text(previous)
        try:
            run('daemon-reload')
            run('restart', 'bluetooth.service')
        except (OSError, subprocess.SubprocessError):
            logging.getLogger('nxbt').exception('Bluetooth rollback could not restart the service')
        raise
