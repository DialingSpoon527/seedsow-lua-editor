# Changelog

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
