#!/usr/bin/env python3
"""Configure R14 and generate exact keyboard entries of at most 32 characters."""
from __future__ import annotations

import argparse
import hashlib
import html
import ipaddress
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BODY_SHA256 = 'c51e7aa1621d7fdd1631d57a334d832b90fc4afc3d0fff3bf992f70c220dde23'


def validate(ip, port, slot, uploader_slot):
    address = ipaddress.IPv4Address(ip)
    if (not address.is_private or address.is_loopback or address.is_unspecified
            or address.is_link_local or address.is_multicast):
        raise ValueError("Use your computer's private LAN IPv4 address, not localhost or a public address.")
    if not 1 <= port <= 65535:
        raise ValueError('TCP port must be between 1 and 65535.')
    if not all(4 <= n <= 120 for n in (slot, uploader_slot)):
        raise ValueError('Both slots must be between 4 and 120. Check that they are unused on the console.')
    if slot == uploader_slot:
        raise ValueError('Choose two different slots: one for the uploader and one for the launcher.')
    return str(address)


def split_body(body):
    # Keep Lua escapes together, without invisible spaces at entry boundaries.
    safe = {0, len(body)}
    i = 0
    while i < len(body):
        if body[i] == '\\' and i + 1 < len(body):
            j = i + 1
            if body[j].isdigit():
                while j < len(body) and j < i + 4 and body[j].isdigit():
                    j += 1
            else:
                j += 1
            safe.add(j)
            i = j
        else:
            i += 1
            safe.add(i)
    valid = {k for k in safe if k in (0, len(body)) or (body[k - 1] != ' ' and body[k] != ' ')}
    best = {len(body): (0, 0.0, None)}
    for start in sorted(valid, reverse=True):
        if start == len(body):
            continue
        options = []
        for end in range(start + 1, min(start + 32, len(body)) + 1):
            if end not in valid or end not in best:
                continue
            count, penalty, _ = best[end]
            options.append((count + 1, penalty + (32 - end + start) ** 2
                            + (0 if body[end - 1] in ';),}]' else 0.2), end))
        if options:
            best[start] = min(options)
    if 0 not in best:
        raise ValueError('Cannot split this uploader into keyboard entries.')
    chunks = []
    start = 0
    while start < len(body):
        end = best[start][2]
        chunks.append(body[start:end])
        start = end
    return chunks


def generate(ip, port, slot, uploader_slot, output_dir):
    ip = validate(ip, port, slot, uploader_slot)
    body_bytes = (ROOT / 'uploader/r14_body.lua').read_bytes()
    if hashlib.sha256(body_bytes).hexdigest() != BODY_SHA256:
        raise ValueError('The tested R14 body has changed. Restore uploader/r14_body.lua before continuing.')
    body = body_bytes.decode('ascii')
    chunks = [f'local PC_IP="{ip}";', f'local TARGET_SLOT={slot};', f'local PC_PORT={port};']
    chunks += split_body(body)
    source = ''.join(chunks)
    if not all(1 <= len(c) <= 32 and c == c.strip() for c in chunks):
        raise ValueError('Generated keyboard entries failed validation.')
    digest = hashlib.sha256(source.encode('ascii')).hexdigest()
    out = Path(output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / 'TYPE_THIS_EXACT.lua').write_bytes(source.encode('ascii'))
    (out / 'ONE_ENTRY_PER_LINE.txt').write_text('\n'.join(chunks) + '\n', encoding='ascii')
    header = ['Type only the characters after |. Keep the cursor at the end between entries.',
              'Do not type row numbers or add spaces or newlines between entries.',
              f'Uploader slot: {uploader_slot}; launcher slot: {slot}; TCP port: {port}',
              f'Entries: {len(chunks)}; characters: {len(source)}; SHA-256: {digest}', '']
    (out / 'TYPE_IN_ORDER.txt').write_text('\n'.join(header + [f'{i:03d} | {c}' for i, c in enumerate(chunks, 1)]) + '\n', encoding='ascii')
    rows = '\n'.join(f'<tr><td>{i:03d}</td><td><code>{html.escape(c)}</code></td>'
                     f'<td>{len(c)}/32</td><td><input type="checkbox" aria-label="Typed row {i}"></td></tr>'
                     for i, c in enumerate(chunks, 1))
    page = f'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>R14 typing sheet</title>
<style>body{{font:16px system-ui;line-height:1.5;max-width:960px;margin:2rem auto;padding:0 1rem;background:#fafafa;color:#222}}
table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccc;padding:8px;text-align:left}}
tr:nth-child(even){{background:#eee}}code{{font:17px ui-monospace,Consolas,monospace;white-space:pre}}
input{{width:22px;height:22px}}.table{{overflow-x:auto}}</style>
<h1>R14 manual entry</h1><p>Uploader slot: <strong>{uploader_slot}</strong>.
Launcher destination: <strong>{slot}</strong>. Computer: {ip}, TCP port {port}.</p>
<p><strong>{len(chunks)} entries, {len(source)} characters.</strong> Type each row's code using
<strong>Keyboard +</strong>. Keep the cursor at the end. Do not add row numbers, line breaks or extra spaces.</p>
<p>Use <strong>Save file</strong> to keep progress. Checkmarks last only while this page remains open;
write down your last completed row before closing it.</p>
<p>Expected final byte count: <strong>{len(source)}</strong>. SHA-256: <small>{digest}</small>.</p>
<div class="table"><table><thead><tr><th>Row</th><th>Type exactly</th><th>Length</th><th>Done</th></tr></thead>
<tbody>{rows}</tbody></table></div></html>'''
    (out / 'VIEW_TYPING_SHEET.html').write_text(page, encoding='utf-8')
    config = {'version': 'R14', 'pc_ip': ip, 'port': port, 'launcher_slot': slot,
              'uploader_slot': uploader_slot, 'characters': len(source), 'entries': len(chunks),
              'source_sha256': digest, 'body_sha256': BODY_SHA256}
    (out / 'config.json').write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')
    return config, out


def ask(label, convert=str):
    while True:
        try:
            value = input(label + ': ').strip()
            if not value:
                raise ValueError('Enter a value.')
            return convert(value)
        except ValueError as error:
            print(error)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ip', help="Computer's private LAN IPv4 address")
    parser.add_argument('--port', type=int, help='Unused TCP port on the computer')
    parser.add_argument('--slot', type=int, help='Unused launcher destination slot, 4-120')
    parser.add_argument('--uploader-slot', type=int, help='Different unused uploader slot, 4-120')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'build')
    args = parser.parse_args()
    values = (args.ip, args.port, args.slot, args.uploader_slot)
    if all(value is None for value in values):
        print("R14 setup: check two unused slots in your console editor before continuing.\n"
              "Use your COMPUTER's IPv4 address. The Switch will connect to it over your LAN.\n"
              'Choose an unused TCP port, preferably 1024-65535. Nothing is sent yet.\n')
        while True:
            values = (ask('Computer IPv4 address'), ask('TCP port', int),
                      ask("Free slot for Alula's launcher", int), ask('Different free slot for the uploader', int))
            try:
                validate(*values)
                break
            except ValueError as error:
                print(f'\n{error}\nPlease enter the settings again.\n')
    elif any(value is None for value in values):
        parser.error('Supply all four settings, or omit them all for interactive setup.')
    try:
        config, out = generate(*values, args.output_dir)
    except (ValueError, OSError) as error:
        parser.exit(1, f'Setup error: {error}\n')
    print(f"\nReady: {config['entries']} entries, {config['characters']} characters.\n"
          f"Uploader slot: {config['uploader_slot']}; launcher slot: {config['launcher_slot']}\n"
          f'Files: {out}\n'
          'Manual entry: open VIEW_TYPING_SHEET.html. Pi upload: use TYPE_THIS_EXACT.lua.\n'
          'Start the sender before running the uploader. See docs/02-existing-editor.md.')


if __name__ == '__main__':
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        raise SystemExit('\nSetup cancelled; no console changes were made.')
