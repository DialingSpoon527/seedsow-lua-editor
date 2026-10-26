# General development and compatible-save tools

For normal installation, [download and restore the prepared save](01-console-install.md).
This page is for modifying compatible saves, developing the editor and building
later updates. Original starter hashes and official release packaging live in
the separate [maintainer guide](../maintainer/README.md).

## Source layout

| Directory | Purpose |
| --- | --- |
| `editor/` | Working console Lua source, compatible-save installation builder and alongside-editor update builder |
| `tools/` | Shared native-save parsers, ASB scripts, global-save editing and target-aware JKSV metadata |
| `pc/` | Optional Python/Tk companion for Windows and the implemented uploader client |
| `pi/` | Optional Raspberry Pi Bluetooth controller bridge, installation and connection export |
| `examples/` | Example Lua programs |
| `tests/` | General runtime, input, PC, HTTP, GUI and packaging checks |
| `maintainer/` | Original reviewed starter validation and official release infrastructure |

Python 3.10+ is needed for these host tools. The PC runtime uses only the standard
library and Tcl/Tk. Lua checks additionally use Lupa's Lua 5.1 runtime. Neither
Python nor Windows nor a Pi is needed to run the installed console editor.

## Build or modify a compatible save

```powershell
python editor/build.py --base "YOUR_BACKUP.zip" --replace-slots
```

`editor/build.py` is a general compatible-save builder. It does **not** require
the reviewed starter's exact hashes. Its input is your own flat JKSV backup ZIP
(or one enclosing backup directory) with `saveg.dat`, manual slot 1 and both
thumbnails. Existing editor backups supply a recognized native launcher. A new
installation instead needs the recognized initial title-screen autosave layout;
arbitrary autosave positions are not supported by the current conversion.
Demo 1.0.0 from the US eShop is the tested reference, not a proven region lock.

`--replace-slots` acknowledges replacement of slots 1-3 on a first installation.
Omit it when rebuilding an existing editor backup. The builder leaves the input
unchanged, retains unrelated files and user programs, and writes a new private
installation ZIP plus a manifest under `build/installer/<build-id>/` by default.
Use `--output PATH` for another new directory. It retains the input backup's
metadata; it does not silently retarget to the original starter title ID.
This structural compatibility check does not establish a new edition's behavior
on a console. Keep custom saves private and test with recoverable backups.

## Troubleshooting a custom build

Check for a manual save in slot 1 with both thumbnails, and one whole backup per
ZIP. First-time custom builds need the recognized initial title-screen autosave
layout; existing editor backups can supply their own recognized launcher. The
tested reference is demo **1.0.0 from the US eShop**, not proof of a US-only
requirement. Other layouts and arbitrary autosave positions are not established.
The builder leaves the input file unchanged when rejecting a backup. Exact
original starter hashes are not a requirement for this general tool.

## Build an alongside-editor update

```powershell
python editor/build_side_editor.py --base "YOUR_EDITOR_BACKUP.zip" --slot 30
```

This produces a Lua program for a fresh user slot, retaining the installed base
loader and recovery slots 1-3. It also accepts `--source` for a combined candidate
core and `--output` for another directory. The input must contain the same base
editor as the console. It can be the original starter you installed; you do not
need a new Switch 2 export merely to target that retained base. Follow
[updates and recovery](04-updates-recovery.md) for loading the generated program.
The alongside-editor workflow passes local checks but still needs its hardware trial.

## Shared format utilities

See [`tools/README.md`](../tools/README.md) for the API map. `IndexedSave` reads the
compressed native object/index layout and applies expected-byte edits while
adjusting offsets. `asb` encodes/decodes version-0 script records. `save_globals`
reads nested length-prefixed variables and checks fixed-width title replacements.
`jksv_metadata` generates portable account-save metadata from explicit target
IDs and sizes without assuming a game or region. These are shared modules used
by both general builders and maintainer scripts; no parser is duplicated.

## Runtime source and recovery

The installed core is composed, in order, from `storage.lua`, `transfer.lua`,
`input.lua` and `editor.lua`. Keep line endings stable: the loader checks the
combined source checksum. Normal launchers load a retained base core and run
the saved source selected by the slot's `.ref` file. Native seed templates let
the editor publish into user slots. Unrestricted Lua can bypass normal storage
protections; backups and recovery entries still matter.

## Local checks

From the repository root:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python tests/smoke_gui.py
python -m pip install -r requirements-dev.txt
python tests/run_checks.py --base "PATH_TO_YOUR_COMPATIBLE_BACKUP.zip"
```

Unit checks cover PC settings, protected destinations, binary preservation,
real HTTP authentication, calibration commands, generated controller macros,
metadata bounds and release-layout guards. The GUI smoke check needs a desktop
and exercises all four tabs and layout without connecting to a Pi.

The Lua runner reads its private input only, uses temporary outputs, and checks
actual editor code through a recording engine: translated input IDs, checksum
and header rejection, all byte values, rebuild preservation, publication, simulated
restart and alongside-editor startup/failure recovery. It has no exact original
starter requirement and needs no game dump. Stand-in results do not establish
new hardware behavior.

On a machine with a POSIX shell:

```sh
sh -n pi/install.sh
```

The original starter's exact hash/privacy regressions, source ZIP allowlist,
publication commands, pinned Pi dependency implementation details and hardware
release checklist are preserved in [maintainer documentation](../maintainer/README.md).
