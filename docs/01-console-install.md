# Install the editor on Switch 2

**This is the first step.** Prepare the editor save on an original Switch, then
transfer that game's save to Switch 2. Once the editor and a saved program load
after a restart, you can do the rest later. A Pi is not needed for installation
or for using the console editor.

If the editor is already installed and working on your Switch 2, skip to
[using the console editor](07-console-editor.md).

## Before starting

You need Seedsow Lullaby **US demo 1.0.0** on both consoles and an original
Switch that already runs a save manager such as [JKSV](https://github.com/J-D-K/JKSV).
Setting up that save manager is outside this guide. The Switch 2 does not need
a save manager for the transfer route below.

Use the same Nintendo Account for the relevant user on both consoles. Put the
consoles near each other and connect both to the internet for the transfer.
Nintendo Switch Online is not required for local save transfer.
[Nintendo's transfer requirements](https://www.nintendo.com/en-gb/Support/Troubleshooting/How-to-Transfer-Your-Save-Data-To-a-Nearby-Console-1549113.html).

Keep an untouched backup before replacing anything. Transferring moves the save
off the source console and can replace an existing save for that game on the
target console. Review the transfer screen before confirming.
[Nintendo's transfer behavior](https://www.nintendo.com/en-gb/Support/Troubleshooting/How-to-Transfer-Your-Save-Data-To-a-Nearby-Console-1549113.html).

## 1. Export a compatible backup from the original Switch

1. Launch the demo and create a manual save in **slot 1**.
2. Close the game and use your save manager to export the whole save.
3. Copy that backup to your PC and ZIP the files from that one backup.
   It should contain `saveg.dat`, `autosave.dat`, `save0001.dat`,
   `save0001.png` and `save0001_s.png`. One enclosing backup folder is accepted.

The builder supports the recognized initial title-screen autosave layout and
existing editor backups. It does not support every arbitrary point in the game.
If it rejects your backup, no input files are changed; see
[backup troubleshooting](05-troubleshooting.md#the-installer-rejects-my-backup).

## 2. Build the editor save on your PC

1. Extract the release folder. Install **Python 3.10 or newer** with Tcl/Tk if
   you do not already have it.
2. Double-click **START WINDOWS.cmd** and select **Install save & updates**.
3. Choose your backup ZIP.
4. Tick **I have a backup and allow replacing slots 1-3**. Those slots become
   the editor and recovery entries. Existing user slots 4-120 are retained.
5. Click **Build installation ZIP**.
6. The app shows the new `Seedsow-Lua-Editor-Save.zip` in
   `build/installer/<build-id>/`. Your input ZIP stays unchanged.

You can close the Pi connection settings; they are optional. The PC builder
works locally without a Pi or a console network connection.

## 3. Restore the editor save on the original Switch

1. Extract the generated ZIP into a new backup folder for Seedsow in your save
   manager's backup directory. Keep all extracted files together. Use the game's
   existing backup directory rather than guessing a title folder.
2. Put that folder on the original Switch's SD card and open the save manager.
3. Select the intended user and Seedsow demo, then restore the new editor backup.
4. Start Seedsow, open **Load**, and load **slot 1**. Its title includes
   **LUA EDITOR**; an unrecognized original menu title may remain until first load.
5. Confirm the editor opens. Its first launch registers the editor/recovery
   entries and available example programs. Close the game normally.

## 4. Move the save to Switch 2

1. On the **original Switch**, open **System Settings > Data Management ?
   Transfer Your Save Data > Send Save Data to Another Console**. Choose the
   intended user and **Seedsow Lullaby demo**.
2. On **Switch 2**, open **System Settings > Data Management > Transfer Your
   Save Data > Receive Save Data**.
3. Confirm the user/game on the transfer screens, then complete the transfer.
   If asked to overwrite an existing target save, only continue once you have
   preserved anything you want to keep.
4. Open the same demo on Switch 2 with the receiving user and load **slot 1**.

These are Nintendo's individual-save transfer menus, not the full system
transfer used when setting up a new console.
[Official step-by-step transfer guide](https://www.nintendo.com/en-gb/Support/Troubleshooting/How-to-Transfer-Your-Save-Data-To-a-Nearby-Console-1549113.html).
Availability depends on the installed software and current transfer support.

## 5. Verify once, then use it whenever you want

1. In the editor choose a free user slot, such as **20**.
2. Use **Keyboard +** or the character grid to enter `print("Hello")`.
3. Choose **Save + publish**.
4. Fully close and reopen the game on Switch 2, then load your numbered slot.
5. Confirm it runs. Load slot **1** or **3** to return to the editor.

**You're set up.** Ordinary editing, saving and running now happen inside the
Switch 2 save. You do not need the original Switch or another save transfer for
each new program. You can stop here and add optional PC uploads or compatible
editor updates later. Preserve the game, its save, recovery slots 1-3 and your
external backup; no software can guarantee recovery after all copies are lost.

Next: [Console editor guide](07-console-editor.md). If you have a Pi,
[optional Windows uploads](02-pi-setup.md) can make entering larger files easier.
