# Seedsow Lua Editor

> [!IMPORTANT]
> **You need an unbanned modded/hacked original Nintendo Switch (Switch 1) for the first installation.**
> It must already be able to run homebrew apps. You will install JKSV on that
> console, restore the ready-made save there, then transfer it to Switch 2.
> **Your Switch 2 does not need to be modded. A Switch 2 by itself is not enough.**

> [!IMPORTANT]
> # This project only runs Lua inside the game
> it has **not** confirmed an Artemis-based path to a broader exploit. 
> Artemis entrypoints are being searched, but installing this 
> editor does **not** guarantee that such a path will work or
> become available. But if it does, you will be able to use it!

## JUST FUTURE-PROOFING? GET THE SAVE ONTO SWITCH 2 FIRST.

> **If you don't know what the rest of this means and just want to keep your
> options open, focus on [installing the editor save on Switch 2](docs/01-console-install.md).
> Confirm that the editor and a saved program load after restarting the game.**
> **Everything else can wait until later.** You do not need to learn Lua, set up
> a Raspberry Pi, configure PC uploads or install editor updates right now.
> Keep the game, its save and recovery slots intact, and keep a backup.

**TLDR *if* an Artemis explot is ever found, and you install this 
on your Switch 2 before any update comes out 
(NOT just Installing the update, you're fricked if it *COMES OUT*)
Then you can use that exploit completely offline.**

**First, get the editor save onto your Switch 2.**
[Download the ready-to-restore save ZIP](https://github.com/DialingSpoon527/seedsow-lua-editor/releases/latest/download/Seedsow-Lua-Editor-Save.zip),
restore it to an original Switch using JKSV, then move that game's save to
Switch 2 with **System Settings > Data Management > Transfer Your Save Data**.
The [installation guide](docs/01-console-install.md) walks through each step.
This initial setup needs an original Switch that can restore saves; putting the
ZIP on a Switch 2 microSD card alone will not install it.

**Once installed and checked after a restart, you're set up for later.** The
editor lives in the game's save: you can write Lua, save programs, and run them
again on Switch 2 without repeating the transfer. You can leave the optional
PC-upload setup and compatible editor updates until whenever you want. Keep
the game and save intact, retain the recovery slots, and keep a backup.

> **Vibecoded:** this project was built with AI assistance, with hands-on testing
> on real consoles. Expect rough edges; it is a community project.

## Start here

**Only have a hacked Switch 1 and no idea what to do next? Follow the
[complete beginner installation guide](docs/01-console-install.md).** It covers
downloading JKSV, copying it to the SD card, backing up the demo, restoring the
ready-made save, and transferring it to Switch 2. You do not need to know Lua.

The short version:

1. Put **JKSV.nro** on the hacked Switch 1's SD card and open it through homebrew.
2. Make a backup of the Seedsow demo's save.
3. [Download **Seedsow-Lua-Editor-Save.zip**](https://github.com/DialingSpoon527/seedsow-lua-editor/releases/latest/download/Seedsow-Lua-Editor-Save.zip)
   and copy that ZIP alongside the backup. **It is already built.**
4. Restore it in JKSV on Switch 1, then use Nintendo's save-transfer menus to
   move the demo save to Switch 2.
5. Load editor slot **1** on Switch 2, restart the game, and load it again.
   **If you only want to future-proof, you can stop here.**

Learn the [console controls](docs/07-console-editor.md) or add the
[optional Pi uploader](docs/02-pi-setup.md) later. No Python, compiling or
save-building step is needed to install the ready-made save.

## The editor works on its own

Use the controller and on-screen character grid, or type into the console's
text-entry dialog with a wired USB keyboard. You can edit Lua, run it, and
save it into numbered slots that remain loadable after restarting the game.
Text and hex modes also let you create and modify ordinary files in the game's
own save storage.

**A Pi is optional.** If you have one, it is a very convenient way to send files
from Windows instead of typing them on the console. The Pi acts as a Bluetooth
controller and the included PC app handles pairing, calibration and sending.
You can add this at any time after installing the editor. Console editing needs
no Pi, PC connection, Wi-Fi or ongoing internet access.

## On the console

<p align="center">
  <a href="docs/images/console-editor.jpg"><img src="docs/images/console-editor.jpg" alt="Console Lua editor showing a program, file controls and the on-screen character grid" width="900"></a>
</p>
<p align="center"><em>Edit, run and save Lua directly on the console.</em></p>

<table>
  <tr>
    <td align="center" width="50%">
      <a href="docs/images/save-menu.jpg"><img src="docs/images/save-menu.jpg" alt="Game load menu showing the editor, recovery entries and saved Lua programs" width="400"></a><br>
      <strong>Editor and program slots</strong><br>
      <sub>Open the editor or load a saved program from the game's menu.</sub>
    </td>
    <td align="center" width="50%">
      <a href="docs/images/included-example.jpg"><img src="docs/images/included-example.jpg" alt="Included Lua example running a blue screen with animated shapes and an elapsed-time counter" width="400"></a><br>
      <strong>Included example</strong><br>
      <sub>The blue animation runs inside the game.</sub>
    </td>
  </tr>
</table>

## What you need

### For the initial installation

- **Seedsow Lullaby US demo 1.0.0** on the source Switch and Switch 2.
- A **modded/hacked Switch 1 that can run homebrew**. The beginner guide explains
  how to add [JKSV](https://github.com/J-D-K/JKSV), the app used to restore the save.
- Your Nintendo Account linked to the relevant user on both consoles, and
  internet access for Nintendo's one-time save transfer.
- A way to copy the extracted save folder onto the original Switch's SD card.
  Download the ready-made ZIP; you do not need the source tools for this step.

### For using the installed editor

Your Switch 2 and controller are enough. A wired USB keyboard makes entering
code much easier. Save the source, choose **Save + publish**, and reload that
numbered slot whenever you want to run it.

### For optional Windows uploads

A Bluetooth-capable Raspberry Pi running compatible Debian/Raspberry Pi OS,
plus Windows and the Pi on the same LAN. A **Pi 3B** was used in testing.
The console only needs Bluetooth for this route; it does not need Wi-Fi.
For the optional PC app, download the companion/source ZIP, install Python
3.10+ with Tcl/Tk, and double-click **START WINDOWS.cmd**.

## Where things are saved

| Console slot | Purpose |
| --- | --- |
| 1 | Main editor |
| 2 | Optional PC-input calibration and receiver |
| 3 | Backup editor |
| 4-120 | Your Lua programs |

Keep slots 1-3. Later editor updates can be installed in a fresh user slot,
leaving the working editor available. Normal editor writes protect recovery
files, retain `.bak` copies of previous readable files, and check saved bytes.
Unrestricted Lua can bypass those protections, so they do not replace a backup.

## Guides

- [Install on Switch 2](docs/01-console-install.md)
- [Use the console editor](docs/07-console-editor.md)
- [Optional: set up a Pi](docs/02-pi-setup.md)
- [Optional: send files from Windows](docs/03-send-files.md)
- [Install later updates and recover](docs/04-updates-recovery.md)
- [Troubleshooting](docs/05-troubleshooting.md)
- [Source, checks and release tools](docs/06-development.md)

## Current status

Manual editing, wired-keyboard input, PC uploads, saving, and running saved
programs after a full game restart have been exercised on real consoles,
including Switch 2. The release also passes local editor, transfer, binary-file,
restart and recovery checks. The new PC/Pi packaging and the optional editor
update still need a fresh hardware trial.

Controller uploads are slow: a small proof takes around a minute, and a 5.6 KB
editor update can take roughly 25-36 minutes. Files can be up to 1 MiB, though
that is a storage limit rather than a practical controller-upload size.

## License

**No credit required.** Project-owned code and documentation are available under
the [BSD Zero Clause license (0BSD)](LICENSE). You may use, modify, share or sell
them without naming the author or keeping this project's copyright or license
notice. The software is provided as-is, without warranty.

This 0BSD permission also applies to project-owned code and documentation in
earlier commits and releases, including versions originally published under MIT.
Existing MIT permissions remain available.

Third-party components and game content retain their own licenses and rights;
see [Third-party notices](THIRD_PARTY_NOTICES.md). For example, NXBT's MIT notice
must still be preserved when distributing NXBT.

The release includes a reviewed starter save and a separate companion/source
ZIP. Keep your own later backups and connection files private.
