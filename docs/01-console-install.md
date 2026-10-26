# Install the ready-made editor save on Switch 2

**You do not need to build anything.** Download
[Seedsow-Lua-Editor-Save.zip](https://github.com/DialingSpoon527/seedsow-lua-editor/releases/latest/download/Seedsow-Lua-Editor-Save.zip),
restore it on an original Switch, then transfer the game's save to Switch 2.
No Python, Raspberry Pi or PC companion setup is needed for this installation.

If the editor is already installed, keep using it. Do not restore the starter
over programs you want to keep. Later improvements can be installed through
[the working editor](04-updates-recovery.md).

## Before starting

You need **Seedsow Lullaby US demo 1.0.0** on both consoles and an original
Switch that already runs a save manager such as [JKSV](https://github.com/J-D-K/JKSV).
Setting up the save manager is outside this guide. The Switch 2 does not need
a save manager for this transfer route.

Link the same Nintendo Account to the relevant user on both consoles. Put the
consoles near each other and connect both to the internet for the transfer.
Nintendo Switch Online is not required for local save transfer.
[Nintendo's transfer requirements](https://www.nintendo.com/en-gb/Support/Troubleshooting/How-to-Transfer-Your-Save-Data-To-a-Nearby-Console-1549113.html).

**Keep a backup before replacing anything.** Restoring the starter replaces this
game's save for the selected user. Transferring moves it off the source console
and can replace an existing save for the game on the target console.
[Nintendo's transfer behavior](https://www.nintendo.com/en-gb/Support/Troubleshooting/How-to-Transfer-Your-Save-Data-To-a-Nearby-Console-1549113.html).

## 1. Download and extract the save

1. Download **Seedsow-Lua-Editor-Save.zip** from the release assets.
2. Extract it into a folder named **Lua Editor**. Inside that folder you should
   see `saveg.dat`, `system.dat`, `save0001.dat`, and many editor files.
3. Keep the files together. Do not place the ZIP on the Switch 2 SD card and
   expect the console to load it directly; it must be restored and transferred.

The separate `seedsow-lua-editor-0.1.1.zip` is the optional PC companion/source
bundle. It is not the save to restore.

## 2. Restore on the original Switch

1. Start the demo once as the intended user so that it has save data, then
   close the game.
2. In JKSV, select that user and the Seedsow demo. Make a backup of the existing
   save and keep an untouched copy.
3. Copy your extracted **Lua Editor** folder into the game's existing JKSV
   backup directory on the original Switch's SD card. For example:
   `JKSV/<the game's existing folder>/Lua Editor/`. The extracted save files
   must be directly inside **Lua Editor**, not another nested folder.
4. Open JKSV again, select the same user and game, select **Lua Editor**, and
   restore it. Review the user/game before confirming.
5. Start Seedsow, choose **Load**, and open **slot 1**, whose title includes
   **LUA EDITOR**. Confirm the editor opens, then close the game normally.

The starter includes recovery entries in slots 1-3 and small examples in slots
4 and 5. Personal account identifiers, input calibration, reports and personal programs
are not included. The required portable restore metadata has blank personal fields.

## 3. Transfer that game's save to Switch 2

1. On the **original Switch**, open **System Settings > Data Management >
   Transfer Your Save Data > Send Save Data to Another Console**. Select the
   intended user and **Seedsow Lullaby demo**.
2. On **Switch 2**, open **System Settings > Data Management > Transfer Your
   Save Data > Receive Save Data**.
3. Confirm the user/game on both transfer screens and complete the transfer.
   Only overwrite an existing target save once anything you want to keep has
   been preserved.
4. Open the same demo on Switch 2 with the receiving user, then load **slot 1**.

Use Nintendo's individual-save transfer, not the full system transfer from
initial console setup. Availability depends on the installed software and
current transfer support.
[Official transfer instructions](https://www.nintendo.com/en-gb/Support/Troubleshooting/How-to-Transfer-Your-Save-Data-To-a-Nearby-Console-1549113.html).

## 4. Check it once, then everything else can wait

1. In the editor choose a free user slot, such as **20**.
2. Use **Keyboard +** or the character grid to enter `print("Hello")`.
3. Choose **Save + publish**.
4. Fully close and reopen Seedsow on Switch 2, then load slot 20 and confirm it
   runs. Load slot **1** or **3** to return to the editor.

**You're set up.** Ordinary editing, saving and running now happen inside the
Switch 2 save. You do not need the original Switch or another transfer for each
new program. Learn Lua, add the optional Pi uploader or install compatible
updates whenever you want. Preserve the game, its save, recovery slots 1-3 and
your backup.

Next: [Use the console editor](07-console-editor.md). If you have a Pi,
[optional Windows uploads](02-pi-setup.md) can make entering larger files easier.

## Optional: custom installation builds

The PC companion still includes an installation builder for maintainers and
people preparing a custom compatible backup. It is not part of the normal
installation above. See [development tools](06-development.md) if you need it.
