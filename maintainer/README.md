# Maintainer and original starter infrastructure

**Not part of installation.** Players download the already-built save and follow
the [beginner guide](../docs/01-console-install.md). They do not provide a clean
autosave, match these hashes, run Python or rebuild a release.

General compatible-save builders remain in [`../editor/`](../docs/06-development.md)
and shared parsers/utilities in [`../tools/`](../tools/README.md). This directory
contains the reviewed original starter and official release machinery only.
Commands below run from the repository root.

## Layout and migration

| Current path | Role | Previous path |
| --- | --- | --- |
| `maintainer/package_save.py` | Validate and package the exact reviewed starter | `tools/package_save.py` |
| `maintainer/check_starter.py` | Starter privacy, hash, structure and actual-Lua regressions | Starter-specific portion of `tests/run_checks.py` |
| `maintainer/package_release.py` | Source/companion ZIP allowlist, checksums and manifest | `tools/package_release.py` |
| `maintainer/publish_release.py` | Git guards, resumable release upload and publication | `tools/publish_release.py` |
| `maintainer/RELEASE_NOTES.md` | Release-page text used by the publisher | Root `RELEASE_NOTES.md` |

Older published source ZIPs retain their original paths. Follow the documentation
included in the ZIP you downloaded; the current tree uses the paths above.

## Preserve the original reviewed starter

```powershell
python maintainer/package_save.py --base "REVIEWED_STARTER_SAVE.zip"
python maintainer/check_starter.py --base "REVIEWED_STARTER_SAVE.zip"
```

A previously released ready-to-restore save ZIP is valid input. The packager
accepts only the reviewed native starter state and matching editor core; it
rejects altered native data rather than publishing someone's personal save.
It removes all unlisted files, personal programs, calibration, reports and
sessions, blanks personal metadata fields, and includes only examples 4 and 5.
It writes `dist/Seedsow-Lua-Editor-Save.zip`, its `.zip.sha256`, and its
`.manifest.json`. Use `--output` to compare a candidate without replacing local
release artifacts. Input ZIPs are read only.

The authoritative `STARTER_HASHES` and reviewed thumbnail hash remain in
[`package_save.py`](package_save.py). All nine native hashes must match. Every
one of 120 launcher seeds is checked against the complete decoded fields and
index; different equivalent zlib encodings are accepted without changing the
reviewed input bytes. Every bootstrap must exactly match canonical generated
code with its validated build identifier and core checksum. Do not relax these
checks to admit another edition or a personal backup.

The original target is demo 1.0.0 obtained from the US eShop, application and
owner ID `0x010042D022AEA000`, with 32 MiB data and 32 MiB journal. This describes
the reviewed artifact, not a US-only runtime requirement. See the
[compatibility investigation](../docs/compatibility.md) before proposing another
target. The full game's catalog ID differs; regional demo IDs remain unresolved.
There is deliberately no `--title-id` switch that bypasses starter review.

Portable JKSV revision-1 metadata remains 86 bytes, beginning with `JKSV` and
revision 1. Account UID bytes 13-28, timestamp bytes 49-56 and commit ID bytes
77-84 are zero. It retains the reviewed public title/owner IDs and sizes. Its
encoder is shared with [the target-aware general utility](../tools/README.md#portable-jksv-metadata),
but the reviewed target is fixed here. Generated metadata and save member bytes
must remain identical to the released starter during structural cleanup.

## Reconstructing from a compatible native backup

The general builder can make a private candidate:

```powershell
python editor/build.py --base "YOUR_COMPATIBLE_BACKUP.zip" --replace-slots --output build/candidate
```

For a first installation, this builder recognizes the initial title-screen
autosave structure and requires manual slot 1 and thumbnails. It also accepts
recognized existing editor launchers and preserves unrelated files on rebuild.
It does not require `STARTER_HASHES`. Its output is a private candidate, not
automatically a reviewed public starter. Only `package_save.py` decides whether
the result matches the original reviewed state and is cleared for publication.

The retained loader combines `storage.lua`, `transfer.lua`, `input.lua`, and
`editor.lua`, then validates its Adler-32 checksum at startup. Three recovery
core/launcher copies provide fallback. User slots retain native seeds and run
the source selected by their `.ref` files. Alongside-editor updates rely on this
base; their generated Lua has isolated settings/reports and startup recovery.
Historical internal V3 labels identify the tested save format, not a requirement
for users to install earlier public releases. The editor payload is unchanged.

## Full validation

```powershell
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -p "test_*.py" -v
python tests/smoke_gui.py
python tests/run_checks.py --base "YOUR_COMPATIBLE_BACKUP.zip"
python maintainer/check_starter.py --base "REVIEWED_STARTER_SAVE.zip"
```

The general runner exercises editing, uploads, all byte values, retained user
files, restart and alongside-editor recovery without exact starter assumptions.
The separate maintainer runner exercises privacy exclusions, every native hash,
launcher structure, equivalent compression, and the packaged starter's Lua.
These use Lupa's Lua 5.1 runtime and a recording engine stand-in; they do not
establish new hardware results. The GUI smoke test needs a desktop session.
With a POSIX shell, also run `sh -n pi/install.sh`.

## Package the companion/source download

```powershell
python maintainer/package_release.py
```

This writes `dist/seedsow-lua-editor-<VERSION>.zip`, a SHA-256 file and member
manifest. Use `--output PATH` for a review candidate. The ZIP has one top-level
`seedsow-lua-editor/` folder, with `START WINDOWS.cmd` beside `pc/`, `pi/`,
`editor/`, `tools/`, `maintainer/`, `tests/`, `docs/` and `examples/`.
Keep these together when extracting. All public files are explicitly allowlisted;
the archive excludes `.git`, `build`, private saves, tokens, connection settings,
downloaded dependencies and unlisted files. Binary images remain byte-identical.
Every member and the archive are checked after writing. The separate installer
ZIP stays flat with 274 save files, including `.nx_save_meta.bin`; it does not
contain the repository or an enclosing directory. Verify both layouts.

Do not add a whole archived workspace to the repository. Custom installations
made from personal backups, generated outputs and connection files stay private.

## Publish a new GitHub release

### Preferred: push a version tag

The [release workflow](../.github/workflows/release.yml) publishes a pushed
`vMAJOR.MINOR.PATCH` tag using GitHub Actions' short-lived repository token.
It requires no personal token or access to a Windows credential store. Update
`VERSION`, the PC version label, release notes and changelog, commit and push
`main`, then tag that reviewed commit:

```powershell
git tag v0.1.2
git push origin v0.1.2
```

Use the actual new version for later releases; do not move a published tag.
The workflow downloads the reviewed 0.1.1 starter and checks its fixed ZIP hash,
runs unit/Lua/starter/GUI/Pi checks, packages the new source, and uses the same
draft/resume/published-asset guards as the local publisher. The unchanged starter
is uploaded byte-for-byte with its existing checksum and manifest. A future
console-payload release must separately review and update that baseline; this
maintenance workflow does not silently rebuild or retarget it.

CI publication requires a matching tag event, `VERSION`, checked-out SHA, remote
tag and a commit already on `main`. It does not push branch changes. The workflow
grants release publication only `contents: write`; its token is not printed or
stored in release assets. Follow progress in the repository's Actions tab. A
failed draft can be resumed by rerunning the workflow without changing the tag.

### Alternative: publish from a signed-in local terminal

Prepare the reviewed save ZIP above, choose a new version in `VERSION` and the
PC version label, update the [release notes](RELEASE_NOTES.md) and changelog,
commit the source to `main`, then use a regular signed-in terminal:

```powershell
python maintainer/publish_release.py
```

The publisher uses Git's credential helper for release API authentication,
verifies remote history, creates the source ZIP, verifies both downloads and
their checksums/manifests, uploads six assets to a draft, and publishes it.
It resumes interrupted drafts using completed asset digests. It does not print
or save plaintext tokens. Existing published versions are never overwritten.
An SSH deploy key can push Git commits, but cannot authenticate release API calls.

Historical initial-publication support remains: to replace only a known first
commit, prepare single-commit local history and pass `--expected-head FULL_SHA`.
The exact force-with-lease refuses any changed remote. Routine updates use normal
pushes. Release tags and already-published ZIPs are not rewritten by a source
reorganization.

## Before a hardware release

Check a tiny Windows proof, console **PC FILE SAVED**, loading its destination
slot, and loading again after a full game restart. Test the new Pi installer
separately from an already-working Pi, and a side editor in a fresh slot with
base recovery retained. Record these as new results; earlier hardware results
do not establish that later packaging changes passed.

The Pi installer pins NXBT at
`ec4b800ad6c55de96bb6c7f9f84b5bdc59a4c975`. `pi/patch_nxbt.py` applies the private
D-Bus connection, continuous-report and player-number compatibility fixes. The
bridge imports only the controller API, not the NXBT web/TUI dependencies.
Fresh installer changes require a separate Pi hardware trial.
