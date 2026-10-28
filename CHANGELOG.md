# Changelog

## 0.1.3 - 2026-10-27

- Record the user's successful console report for the current fresh-save build
  on 2026-10-27; detailed feature coverage and new PC/Pi trials remain unrecorded.

- Make the sysNAND requirement explicit: download and transfer in stock mode;
  use CFW on that same sysNAND only for JKSV. Explain that emuNAND saves are separate.

- Document the reported NSO cloud route from demo or full game to a full-game
  target on Switch 2. Keep demo-to-demo nearby transfer as the beginner path:
  no full game or NSO membership required, but Nintendo connectivity is required.

- Add the dated 23.0.1 preparation checkpoint and same-account requirement;
  separate Switch 2 setup from Switch 1 stock/CFW sysMMC stages. Retain the
  manual-save requirement before JKSV. Correct the reported demo region to EU.
- Correct the documented Switch keyboard limit to 32 characters per dialog and
  enforce it in the recording engine. Longer test edits use separate manual
  insertions; `textfieldsize` does not change the native keyboard's limit.
- Tap code to place the cursor using native text measurements. Select the code
  window with A for D-pad cursor movement and B to leave without deleting text.
  Show a light left-edge line on hover/focus and a black line while selected.
- Make the current editor the default in fresh saves, including slots 1 and 3
  and user-program launchers. Keep alongside updates for existing installations.
- Move navigation into a full toolbar row, increase text-layer height, and
  refresh font geometry after modal calibration. Remove redundant button hints.
- Scope PC build completion/error state to its worker; remove the unused keyboard
  transfer wrapper and duplicate controller fallback polling.
- Label the Switch save and optional PC bundle separately; rename the latter
  `Seedsow-PC-Companion-and-Source-VERSION.zip`. Keep beginner installation first
  and document keyboard, controller-grid, Pi and save-restore update routes.
- Replace candidate-source text patching with directly editable Lua modules;
  freeze and hash the reviewed V3 recovery core separately.
- Add repeatable `--include-save` packaging for a fresh update slot, preserving
  every backup member and refusing occupied slots or existing output.
- Accept enclosing JKSV backup folders for updates and normalize candidate line
  endings so Windows CRLF does not break reconstruction checksums.
- Add line-up/down cursor movement, independent line/page scrolling and reliable
  cursor following to the editor. Long lines follow the cursor horizontally;
  the preview displays line numbers. Hardware testing is pending.
- Show a visible `[|]` insertion marker and use standard Switch/game input
  aliases without mandatory calibration. Keep learned mappings as an optional
  fallback and retain them on restart.

## 0.1.2 - 2026-10-26

Maintenance release: the prepared console save is byte-identical to 0.1.1.
Existing users do not need to reinstall or restore anything.

- Lead with the prepared-save installation and console editing; clarify account,
  Nintendo connectivity, sysMMC/emuMMC and optional PC/Pi requirements.
- Record tested versus untested editions and the title-ID investigation without
  claiming that US-only compatibility is established.
- Separate reviewed-starter and release infrastructure into `maintainer/`, retain
  general builders in `editor/` and shared save tools in `tools/`, and split
  starter-specific regressions from general compatible-save checks.
- Share a target-aware JKSV metadata encoder while preserving the reviewed
  starter's exact target, native hashes, launcher checks and installed bytes.
- Include console screenshots and 0BSD licensing with no attribution requirement
  for project-owned code and documentation.
- Publish tagged releases through GitHub Actions using its repository token.
- Size the companion's minimum window from the host theme/fonts so controls
  remain visible with larger fallback fonts.

## 0.1.1 — 2026-10-26

- Adds a ready-to-restore starter save as the main download. Users no longer
  need to build a save or install Python to complete the initial console setup.
- Clears personal account fields and limits the starter to reviewed editor
  assets and included examples.
- Makes source tools and Pi uploads optional in the installation instructions.

## 0.1.0 - 2026-10-26

Initial release of this vibecoded, AI-assisted console Lua editor.

- On-console text and hex editing, wired-keyboard entry and an on-screen grid.
- Persistent Lua program slots, backup editor entries and file recovery copies.
- PC tool to build an installation save from a compatible owner-supplied backup.
- Optional Windows-to-console uploads using a Raspberry Pi Bluetooth controller.
- Alongside-editor update builder for later improvements.
- Installation, everyday use, optional uploads and recovery guides.

The core editing/upload/save/restart flow has real-console results, including
Switch 2. The repackaged PC/Pi setup and alongside-editor update still need a
fresh hardware trial.
