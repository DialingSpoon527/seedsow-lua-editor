# Seedsow Lua Editor @@VERSION@@

**New users: download the Switch save ZIP first.** The editor runs inside
Seedsow on your console. The Windows companion is an optional separate download.

**Preparation firmware checkpoint:** use **23.0.1 on both consoles while it is
the current firmware** (checked 2026-10-27). If a newer firmware appears, stop
before updating and check the installation guide for updated project advice.
The future FS preparation path can change even if the Lua editor keeps working.

## 1. Switch download: Seedsow-Lua-Editor-Save.zip

This is an already-built **game save**, ready to restore with JKSV. You do not
need Python, a build step or a Raspberry Pi for the initial installation.

**Use sysNAND/sysMMC, not emuNAND/emuMMC.** Download the game and transfer the save
in stock mode. Only JKSV backup/restore needs CFW on that same sysNAND; stock and
CFW sysNAND share saves, while emuNAND has separate saves.

1. Use a hacked Switch 1 that can run JKSV and complete Nintendo's official save
   transfer. Your Switch 2 does not need to be hacked.
2. In stock sysMMC on Switch 1, make an in-game save and close Seedsow.
3. Boot CFW on that same sysMMC for JKSV backup/restore of
   **Seedsow-Lua-Editor-Save.zip**, then return to stock sysMMC and load slot 1.
4. Transfer that user's game save to Switch 2 using the same Nintendo Account.
5. **Preparation is complete when the transfer finishes.** Keep the game, its
   save, recovery slots and a backup. Loading the editor on Switch 2 can wait.

[Beginner installation guide](https://github.com/DialingSpoon527/seedsow-lua-editor/blob/v@@VERSION@@/docs/01-console-install.md)

If you only want the editor installed for later, stop here and keep a backup.
Use the controller character grid or a wired USB keyboard to edit on the console.
The editor itself needs no Nintendo connection. The initial official save transfer
also requires Nintendo connectivity and account verification.

**Nearby/local transfer works with the demo on both consoles:** no full game or
NSO membership is needed, but both consoles must connect to Nintendo's servers.
**Keep matching editions: demo → demo or full game → full game. A demo save
cannot be transferred to the full game.** If you own the digital full game,
**Online License** lets the purchasing user launch it on Switch 1 while online
without loading its virtual game card there. Restore and transfer its full-game
save to the same full game on Switch 2. Online License authorizes game access;
**NSO Save Data Cloud** separately requires a membership to copy that same
full-game save. Neither feature converts a demo save.

The prepared save opens the current editor directly in **slot 1**. Slot 2 is
the optional upload receiver; slot 3 is a backup of the current editor. Programs
use slots 4-120. No slot-30 setup is needed for a fresh installation.

## 2. Optional PC download: Seedsow-PC-Companion-and-Source-@@VERSION@@.zip

Extract this ZIP **on your computer**. Open **START WINDOWS.cmd** for the Windows
companion; Python 3.10+ with Tcl/Tk is required. The bundle also contains Lua
source, development tools, documentation and the optional Raspberry Pi bridge.

Use it for PC/Pi uploads or to build an editor update for your retained base.
It is not a Switch save: do not restore it with JKSV. Older releases called this
bundle `seedsow-lua-editor-VERSION.zip`. GitHub's automatic **Source code**
archives are for development and are also not console saves.

## Already installed? Keep your save and update from the console

Do not restore the starter over programs you want to keep. A compatible editor
update is an ordinary Lua file, built for a particular fresh user slot. Keep
recovery slots 1-3 and your last working editor.

- **Wired USB keyboard:** enter the update source with **Keyboard +** in chunks,
  then **Save + publish** and load its matching slot.
- **Controller only:** enter the same source with the on-screen grid and publish.
  This works without a Pi but takes substantial manual entry.
- **Optional PC/Pi:** upload the Lua file into the matching fresh slot, wait for
  **PC FILE SAVED**, then load it.
- **JKSV restore:** a complete update save ZIP replaces the console save with
  that ZIP's contents. Back up first; programs absent from it will not be kept.

[Update methods, obtaining the Lua file, and recovery](https://github.com/DialingSpoon527/seedsow-lua-editor/blob/v@@VERSION@@/docs/04-updates-recovery.md)

The current editor adds tap-to-position, a selectable code window for D-pad
cursor movement, line movement, independent scrolling and a visible insertion
cursor. A left-edge line is light on hover/focus and black while selected; B
leaves cursor mode. Ordinary controller aliases work without mandatory calibration. It uses
directly editable Lua modules and separate settings/reports. Automated checks
cover editing, publication, restart, reconstruction failure and startup recovery.
**The 0.1.3 fresh-save build was reported working on console on 2026-10-27.**
**The 0.1.3 alongside-update workflow was reported working on 2026-10-28:** a user
built an update for another slot using their original installation as the base,
transferred the full editor via Mac/Raspberry Pi and ran it on console.
A fresh PC/Pi installation trial remains pending.

The tested reference is demo 1.0.0 from the US eShop on Switch 1 and Switch 2.
Japanese demo, EU demo and US full-game working cases are user reports; see
[compatibility evidence](https://github.com/DialingSpoon527/seedsow-lua-editor/blob/v@@VERSION@@/docs/compatibility.md).

Project-owned code and documentation use 0BSD with no credit required. Built
with AI assistance and console testing.
ZIP downloads include SHA-256 files and manifests; neither is another installer.
