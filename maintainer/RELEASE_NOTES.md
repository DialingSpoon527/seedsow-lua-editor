# Seedsow Lua Editor 0.1.2

**Maintenance release: existing users do not need to reinstall, restore a save,
or update the console editor.** The prepared save ZIP is byte-identical to 0.1.1.
This release updates the companion/source bundle, installation guidance and
repository organization. Do not overwrite an existing save containing programs
you want to keep.

Changes include clearer prebuilt-save installation, corrected account/networking
and compatibility guidance, console screenshots, and 0BSD licensing (no credit
required for project-owned code and documentation). General save tools remain
accessible; original starter validation and release infrastructure are separated
under `maintainer/`. Other game editions still need compatibility testing.

## Main download: Seedsow-Lua-Editor-Save.zip

**The save is already built. Download it, restore it on a modded/hacked Switch 1
using JKSV, then transfer the game's save to Switch 2. No Python, compiling,
save building or Raspberry Pi is required for the initial setup.**

**A modded/hacked Switch 1 with homebrew is required for the initial restore.**
Your Switch 2 does not need to be modded. The beginner guide covers installing
JKSV, making a backup, copying the ready-made ZIP, restoring it and transferring.

[Step-by-step installation guide](https://github.com/DialingSpoon527/seedsow-lua-editor/blob/v0.1.2/docs/01-console-install.md)

If you only want to future-proof, get the save onto Switch 2 and confirm it
loads after restarting the game. Everything else can wait. Keep the game, save,
recovery slots and a backup intact.

The ready-made starter contains the editor, recovery entries and two examples.
Personal account identifiers, calibration, reports, sessions and personal
programs are excluded. Portable JKSV restore metadata has blank personal fields.
Tested reference: **Seedsow Lullaby demo 1.0.0 from the US eShop**. Other regional
demos, the full game and other versions remain untested, not proven incompatible.

The matching Nintendo Account is required for the save users in the official
transfer, not inherently for downloading the demo. Both consoles need Nintendo
connectivity for that initial transfer; blocking Nintendo servers beforehand can
prevent it. The documented source is online-capable sysNAND/sysMMC; an isolated
emuMMC normally blocks those servers. This is a workflow choice, not a physical
NAND restriction of the transfer feature, and CFW on sysNAND is not ban-proof.
Running the installed editor afterward requires no Nintendo connection.

## Optional download: seedsow-lua-editor-0.1.2.zip

This is the PC companion and source bundle. Download it if you want the optional
Pi uploader, development tools or later update-building tools. The installed
console editor works with its controller/character grid or a wired USB keyboard
without any of those extras.

Windows and Raspberry Pi describe the implemented uploader, not a fundamental
Lua runtime requirement. General save tools remain in `tools/` and `editor/`;
reviewed-starter and release infrastructure is in `maintainer/`.

**Vibecoded:** built with AI assistance and hands-on console testing. The core
editor/save/restart flow has real-console results, including Switch 2. The new
PC/Pi packaging and alongside-editor update still need a fresh hardware trial.

An Artemis-based route to a broader exploit has not been confirmed by this
project. Installing the editor does not guarantee that a future exploit path
will work or become available.

Both downloads include SHA-256 checksum files and file manifests. If you already
have the editor installed, keep your existing save and programs; do not restore
the starter over them.
