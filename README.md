# Seedsow Lua Editor

**First, get the editor save onto your Switch 2.** Build the save on your PC,
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

1. [Download the release](https://github.com/DialingSpoon527/seedsow-lua-editor/releases/latest)
   and extract `seedsow-lua-editor-0.1.0.zip` on your PC.
2. [Install the editor save on Switch 2](docs/01-console-install.md).
3. [Write and save your first program on the console](docs/07-console-editor.md).
4. If you have a Raspberry Pi, optionally [set up PC uploads](docs/02-pi-setup.md).

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

## What you need

### For the initial installation

- **Seedsow Lullaby US demo 1.0.0** on the source Switch and Switch 2.
- An original Switch with a working save manager such as
  [JKSV](https://github.com/J-D-K/JKSV), plus a compatible backup to build from.
- Your Nintendo Account linked to the relevant user on both consoles, and
  internet access for Nintendo's one-time save transfer.
- A PC with **Python 3.10+**, including Tcl/Tk, to build the installation save.
  On Windows, double-click **START WINDOWS.cmd**; no pip packages or WSL are needed.

### For using the installed editor

Your Switch 2 and controller are enough. A wired USB keyboard makes entering
code much easier. Save the source, choose **Save + publish**, and reload that
numbered slot whenever you want to run it.

### For optional Windows uploads

A Bluetooth-capable Raspberry Pi running compatible Debian/Raspberry Pi OS,
plus Windows and the Pi on the same LAN. A **Pi 3B** was used in testing.
The console only needs Bluetooth for this route; it does not need Wi-Fi.

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

[MIT license](LICENSE) > [Third-party notices](THIRD_PARTY_NOTICES.md).
Installation ZIPs are built from your own save and should stay private; share
the source release instead.
