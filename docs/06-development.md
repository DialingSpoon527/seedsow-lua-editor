# Source, checks and releases

The Windows runtime uses only Python's standard library. Lua regression checks
need Lupa's Lua 5.1 runtime. They use a recording engine stand-in; they do not
prove new hardware behavior.

## Local checks

From the repository root:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python tests/smoke_gui.py
```

The first command tests PC settings, protected destinations, binary preservation,
real HTTP authentication, calibration commands and actual generated controller
macros. The GUI smoke check requires a desktop environment and tests all four
tabs, binary handling and page layout without connecting to a Pi.

To check actual Lua source, packaging and simulated restart:

```powershell
python -m pip install -r requirements-dev.txt
python tests/run_checks.py --base "PATH_TO_YOUR_COMPATIBLE_BACKUP.zip"
```

Your private input is read only. Generated fixtures and results use a temporary
directory. Checks include the editor, translated input IDs, checksum and header
failures, raw bytes, rebuilding while retaining user files, and side-editor
publication/startup/restart/failure recovery. No game dump is needed.

On a machine with a POSIX shell, also check the Pi installer syntax:

```sh
sh -n pi/install.sh
```

The Pi installer pins NXBT at
`ec4b800ad6c55de96bb6c7f9f84b5bdc59a4c975`. `pi/patch_nxbt.py` contains the
private D-Bus connection, continuous-report and player-number controller compatibility fixes.
The bridge imports the controller API only; the NXBT web/TUI dependencies are
not installed. Verify changes to this installer with a fresh Pi hardware trial.

## Command-line builders

```powershell
python editor/build.py --base "YOUR_BACKUP.zip" --replace-slots
python editor/build_side_editor.py --base "YOUR_EDITOR_BACKUP.zip" --slot 30
```

Omit `--replace-slots` when rebuilding an existing editor backup. The builders
write to `build/` by default and report the output location as JSON. The side
builder also accepts `--source` for a combined candidate core and `--output`
for a different output directory.

The installed editor core is composed, in order, from `storage.lua`, `transfer.lua`,
`input.lua` and `editor.lua`. Keep line endings stable: the loader checks the
combined source checksum. Normal user launchers load a retained base core and run
the saved source selected by the slot's `.ref` file.

## Create a shareable source ZIP

```powershell
python tools/package_release.py
```

This writes `dist/seedsow-lua-editor-0.1.0.zip`, its SHA-256 file, and a member
manifest. The packager uses an explicit file allowlist and validates the ZIP
after writing. It excludes `.git`, `build`, credentials, private save files,
downloaded dependencies and unlisted files even if present in the repository.

Share the source ZIP or the curated Git repository. Generated installation
ZIPs contain the owner's save data and should stay private. Build outputs and
local settings are ignored by Git. Do not add a whole archived workspace to
the repository.

## Publish a GitHub release from the command line

After committing the prepared source to `main`, run from a regular signed-in
terminal:

```powershell
python tools/publish_release.py
```

The tool uses Git's configured credential helper, verifies the remote commit,
builds the ZIP, uploads the ZIP/checksum/manifest to a draft release, and then
publishes it. It does not print or save a plaintext token. Existing published
versions are not overwritten. To replace the repository's initial commit, first
prepare a single-commit local history and pass `--expected-head` with the full
known old SHA. The force push uses that exact lease and refuses a changed remote.

## Before a hardware release

Check a tiny Windows proof, console **PC FILE SAVED**, loading the intended slot,
and loading it after a full game restart. Test the new Pi installer separately
from compatibility with an already-working Pi. Test a side editor in a fresh
slot while retaining base recovery entries. Record these as new results; a
prior hardware result does not establish that later packaging changes passed.
