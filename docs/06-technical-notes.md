# Technical notes

## Pico controller validation

The controller sender supports the pinned switch-pico UART v3 firmware and
the level-preserving HTTP controller interface. Offline checks reconstruct a
complete SSE2 file packet from simulated UART button-clock edges and verify
its contents and checksum. They also cover partial UART writes, interruption,
HTTP errors, protected destinations, and releasing buttons after a lost reply.

The final November 19, 2026 test run passed all 25 tests, including the three
Lua 5.1 installer simulations with the pinned Lupa 2.8 development dependency.
Shell syntax, Python syntax, documentation file links, and heading links were
checked as well.

The updated Pi service preserves the companion API while selecting the actual
available adapter, waiting for pairing-agent readiness, retaining an active
transfer until its worker queues cancellation, and reporting malformed requests.
The dependency patcher retains continuous reports and private D-Bus connections,
adds socket-reset recovery and correct peer-address recording, and exposes
profile registration errors. Its Bluetooth helper changes only the Input-plugin
setting, retains existing explicit disabled plugins, refuses foreign/wildcard
configurations, and attempts rollback if the Bluetooth restart fails.

The exact pinned dependency was patched twice identically and parsed locally.
Pi state, HTTP, and systemd tests use simulated devices and temporary files.
The revised Pi installation and real Bluetooth pairing still require hardware
validation. They do not establish a fix for a particular BlueZ/GATT failure.

The new Pico path still requires a physical button test, calibration, and a
complete file transfer on the console. Its pinned RP2040 UF2 is identified in
the Pico guide. Serial writes alone provide no console acknowledgement.

The November 20 Pico 2 W addition builds that same pinned UART source with
Pico SDK 2.2.0, board `pico2_w`, platform `rp2350-arm-s`, 150 MHz stock clock,
and one controller interface. No upstream firmware source changes or sender
wire-format changes were needed. The included UF2 passes picotool image/board
inspection and the structural checker in `tools/check_pico2w_firmware.py`.
Its build recipe and dependency notices are in `firmware/pico2w/`. This is an
offline build result; no board was flashed and no console was contacted for it.
The AIO Bluetooth backend and Wi-Fi HTTP service are not included in this build.
All 29 tests passed after this addition, including Lua 5.1 installation
simulations, UART packet reconstruction, and malformed/wrong-chip UF2 rejection.

## Scope and provenance

The installer prepends your computer address, TCP port and destination slot to
the compact bootstrap. Generate configured source through `tools/make_sheet.py`.

The compact native body is retained **byte for byte**, without added fail-safes:

```text
uploader/bootstrap.lua
3599 bytes
SHA-256 c51e7aa1621d7fdd1631d57a334d832b90fc4afc3d0fff3bf992f70c220dde23
```

It is kept small for manual entry. `.gitattributes` disables text conversion for
this file, and generation verifies its hash. It needs three prepended settings:
`PC_IP`, `TARGET_SLOT` and `PC_PORT`. The generator preserves the original chunk
splitting rules and never splits a Lua byte escape between keyboard entries.

Desktop changes include interactive setup, distinct uploader/destination slot
validation, a pinned archive checksum, clearer connection errors, byte progress,
separate generated manifests, and a per-attempt install-log ID. The native
connection/read loop remains minimal, including its lack of timeouts and error
handling. Host socket timeouts cannot unfreeze a blocked console receiver.

## Hardware evidence

The handoff reports a successful Switch 1 install and HTTP `/status` response,
plus successful manual uploader entry and installation on an unmodified Switch 2.
Exact editor version, game region and firmware for each test were not supplied.
Switch 1 native experiments used emuMMC; this is distinct from the **sysMMC**
workflow needed when transferring a replacement save through stock mode.

Those reports apply to the supplied uploader workflow. No new console hardware trial
has been performed for this repository cleanup. In particular, validate the
revised streamed installer/log ID and the complete Pi route on hardware before
calling this revision hardware-tested. Offline checks exercise generation,
framing, installer checks and upstream patch compatibility; they do not execute
the native exploit.

Alula's current
[README](https://github.com/alula/switch-artemis-launcher#supported-games)
documents the Seedsow demo and says the full game is unsupported. Do not inherit
the old editor's full-game compatibility claim for this launcher.

## Upstream version

The PC fetches the original
[v1 seedsow_save.zip](https://github.com/alula/switch-artemis-launcher/releases/download/v1/seedsow_save.zip):

```text
SHA-256 d9f3d0204860aa9764106c54b18d2b226dd525d72fbfea6bd7a706e9cfeef76e
```

It checks the hash before opening the ZIP. Required source patches must each
match the expected upstream text. A newer release needs a reviewed adapter,
not a removed checksum check. `--release` accepts the same unchanged v1 archive
from disk, making the transfer independent of internet access after download.

## Installed files and slot registration

The sender adapts five upstream files to the `ax_` namespace:

```text
ax_core.lua
ax_http.lua
ax_inject.lua
ax_exploita.lua
ax_proggy.ttf
```

For destination NNN, it adds `ax_slotNNN.lua`, `ssslotNNN.ref`,
`saveNNNN.dat`, `saveNNNN.png` and `saveNNNN_s.png`. Number formatting is a
three-digit slot in `ax_slot`/`ssslot` and a four-digit slot in `save` filenames.
It reads existing `ssNNN.asb`, `ssseedNNN.bin` and `ssethumb.png` editor resources.

The installer refuses occupied destination files and differing shared launcher
files. It checks all received lengths/checksums and shared-file conflicts before
writing payload files, verifies writes by readback, and writes the slot reference
last. The ordinary editor registers that reference when loaded next.

It does not directly replace `saveg.dat`, `system.dat`, `autosave.dat`, `inject.iet`,
`save9999.dat` or editor recovery sources. Loading the editor can update normal
menu metadata. Installation is **not transactional**: an interruption after
writes start can leave files behind, and an occupied partial destination is
refused on a retry. Keep a backup and inspect an interrupted attempt.

`ax_install.log` includes the run ID printed by the current sender, plus either
`ARTEMIS_INSTALL_COMPLETE SLOT=... RUN=...` or `ARTEMIS_INSTALL_FAILED ...`. Log matching prevents a stale
success from being treated as confirmation of a later send. The TCP sender
does not receive an install acknowledgement.

## Commands

Interactive setup works on Windows with `py`, or Mac/Linux with `python3`:

```sh
python3 tools/make_sheet.py
python3 pc/send_alula.py
```

For scripted setup, replace every capitalized argument with your actual setting:

```sh
python3 tools/make_sheet.py --ip YOUR_PC_IPV4 --port YOUR_TCP_PORT --slot YOUR_FREE_LAUNCHER_SLOT --uploader-slot YOUR_FREE_UPLOADER_SLOT
```

Additional sender options:

| Option | Purpose |
| --- | --- |
| `--config PATH` | Load a generated settings file outside the default `build/` |
| `--release PATH` | Use the unchanged pinned v1 ZIP from disk |
| `--prepare-only` | Validate/prepare files without opening a listening socket |
| `--out DIR` | Write the local stage and sender manifest somewhere else |
| `--port PORT` | Advanced explicit port mode, without automatic config loading |
| `--listen ADDRESS` | Override the listen interface; default is the configured computer IP |

Use an explicit `--config` when overriding `--port` if you want the settings
cross-check. The Switch's generated `TARGET_SLOT` remains authoritative; the
sender's slot display is only a reminder.

Typing outputs and `config.json` are local settings. `stage1_install.lua` and
`sender-manifest.json` are separate sender outputs, so preparation does not
overwrite the typing configuration. Everything defaults to ignored `build/`.

## HTTP differences and recovery

The sidecar redirects launcher/core/font references to `ax_` files and adds the
editor recovery sources to the HTTP protected-file list. User programs are still
files: HTTP write/eval access is powerful and not a complete safeguard against
damage to the save.

Update overrides are `ax_inject2.lua`, `ax_core2.lua` and `ax_http2.lua`.
Holding Minus during slot load skips the launcher override and propagates
recovery to core/payload overrides. Pressing Minus on the launcher screen can
also enable core/payload recovery before a selection. The adapter corrects the
upstream message that otherwise asks for a second Minus press.
See [Alula's upstream update and HTTP documentation](https://github.com/alula/switch-artemis-launcher#updating).

The temporary installer is console-to-PC TCP; Alula's later HTTP connection is
PC-to-console on port 8080. Neither is the Pi companion's LAN HTTP connection
to its controller bridge on port 39391.

## Local validation

Run the standard-library checks from the project folder:

```sh
python3 -m unittest discover -s tests -v
```

For the Lua 5.1 installer simulations, first install the optional development
dependency with `python3 -m pip install -r requirements-dev.txt`. Without it,
those tests are reported as skipped. Neither setup nor the sender needs it.

To check actual upstream compatibility without starting a console session:

```sh
python3 pc/send_alula.py --port YOUR_TCP_PORT --prepare-only
```

The second command downloads the pinned archive. Native calls, Wi-Fi behavior
and game compatibility require a console trial.
