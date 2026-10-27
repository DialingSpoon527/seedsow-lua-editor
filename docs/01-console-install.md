# Beginner guide: get the editor save onto Switch 2

## Read this first

**A modded/hacked Switch 1 is required.** It must already be able to open the
homebrew menu, where unofficial apps run. This guide starts from that point;
it does not teach you how to hack a console.

**The Switch 2 does not need to be modded.** You use the hacked Switch 1 to
restore the prepared save, then Nintendo's normal save-transfer feature moves
that game's save to Switch 2. A stock Switch 1 or a Switch 2 alone cannot do
this initial restore.

**You do not need to build anything, write code, install Python or own a Pi.**
The editor save is already made for you.

## What to have ready

- Your hacked Switch 1, including its microSD card and working homebrew menu.
- Your Switch 2.
- A computer and a way to read the Switch 1's microSD card on it. A microSD card
  reader or SD adapter is enough. The file-copy steps below use Windows names.
- The same Seedsow Lullaby edition installed on both consoles. The tested
  reference used in this guide is **demo 1.0.0 obtained from the US eShop**.
  There are also user-reported working cases for the **Japanese demo**,
  **UK demo** and **US full game**; see [compatibility notes](compatibility.md)
  for the distinction between reference testing and community reports.
- The same Nintendo Account linked to the user you will use on each console.
- Internet access on both consoles for the save-transfer step.

The matching account is for the **save users and Nintendo's transfer process**.
It is not inherently required that this account downloaded the demo. Each selected
user must be able to launch the installed demo.

### Check the source setup before restoring

The documented workflow uses an **online-capable sysNAND/sysMMC** (the original
console's internal system storage) with a real linked Nintendo Account. The
restored save must be in the same system environment used for transfer. An
isolated **emuMMC** (a separate system environment usually on the SD card) normally
blocks Nintendo servers and cannot complete the official transfer in that state.
Restoring into emuMMC does not also restore into sysMMC.

This describes the workflow, **not a technical requirement that the transfer
feature itself run on physical NAND**. If you only have an isolated emuMMC,
understand your setup before proceeding rather than taking it online blindly.
CFW on sysNAND is not ban-proof; an unbanned console is not a guarantee against
a future ban.

Both consoles need Nintendo connectivity and account verification for the initial
transfer. **Blocking Nintendo servers beforehand can prevent it.** Nintendo also
specifies current system software for transfer; if prompted to update, decide
whether to proceed before continuing. This project cannot guarantee ongoing
transfer availability. After installation, the editor runs without Nintendo
connectivity. See [Nintendo's requirements](https://www.nintendo.com/sg/support/switch/secondary/transfer.html)
and [compatibility notes](compatibility.md).

If you already installed this editor, keep your existing save. Do not restore
the starter over programs you want to keep.

## 1. Get the demo on both consoles

1. On both consoles, make sure you can open the same Seedsow Lullaby **demo**.
   If needed, obtain it through Nintendo eShop using an account with access.
   The download account need not be the user whose save will be transferred.
2. Highlight the demo on HOME and press **+** to see its version. This project
   tested **1.0.0 from the US eShop**. Working cases have also been reported for
   the **Japanese demo**, **UK demo** and **US full game**, without exact version
   or feature details. These reports have not been independently reproduced by
   the maintainer. This guide follows the demo reference workflow.
3. On both consoles, link the intended save user to the same Nintendo Account.
   On Switch 1, use the online-capable system environment described above.
4. On Switch 1, start the demo as the user whose save you will transfer, then
   choose **New Game**.
5. Hold **R** to skip through the opening until you reach normal dialogue.
6. Release **R**, then press **ZL** to open the **save menu**.
7. Choose an empty save slot (**slot 1** is fine), confirm **Save**, and wait for
   saving to finish. Opening the save menu alone does not create a save.
8. Press **HOME**, highlight the game, press **X**, and choose **Close**.
   Leave the game closed while working in JKSV.

**Make at least one in-game save before opening JKSV.** JKSV will only recognize
the game for that user after a save has been made. Simply reaching the title
screen or opening the save menu is not enough.

## 2. Download two files on your computer

1. Download [**JKSV.nro** from JKSV's official release](https://github.com/J-D-K/JKSV/releases/latest/download/JKSV.nro).
   This is the save-manager app for your hacked Switch 1. It is not a Windows
   program, so do not try to open it on the computer.
2. Download [**Seedsow-Lua-Editor-Save.zip**](https://github.com/DialingSpoon527/seedsow-lua-editor/releases/latest/download/Seedsow-Lua-Editor-Save.zip).
   This is the already-built editor save. **Leave this file as a ZIP.**

Ignore the separate companion/source ZIP for now. You only need the two files
above for the initial installation.

## 3. Put JKSV on the Switch 1 SD card

1. On Switch 1, hold **POWER** until the power menu appears, then choose
   **Power Options > Turn Off**. Sleeping the console is not the same as turning
   it off for removing its SD card.
2. Remove its microSD card and put it into the computer's card reader.
3. In **File Explorer > This PC**, open the SD card's drive. The top level of
   that drive is the card's root. If Windows asks to format the card, cancel;
   do not format your existing modded-console card.
4. Open the folder named **switch**. If it does not exist, create a folder with
   that exact name at the top level of the card.
5. Copy the downloaded **JKSV.nro** into that folder. The result should be:

   ```text
   SD card/
     switch/
       JKSV.nro
   ```

6. Eject the SD card in Windows, remove it from the reader, and put it back into
   the powered-off Switch 1.
7. Boot the same homebrew-capable system environment you will use for the save transfer.

You have installed JKSV. You have not restored the editor save yet.

## 4. Open JKSV and back up the demo

If the demo does not appear in JKSV, go back to step 1 and make the first
in-game save: **New Game > hold R until normal dialogue > release R > ZL to open
the save menu > choose an empty slot and save**. Close the game, then reopen JKSV
under that same user.

1. Open your Switch 1's **homebrew menu**. On many setups, opening **Album** from
   HOME opens it. Other setups use holding **R** while starting an installed
   game. Use the homebrew entry method your modded setup provides.
2. Select **JKSV** and press **A** to open it.
3. Select the user linked to the Nintendo Account you will use for transfer,
   then select the **Seedsow Lullaby demo**.
4. In the backup list, highlight **New** and press **A**. If it asks for a name,
   enter **Before Lua Editor**. If it names the backup automatically, note the
   name it gives you. Confirm and wait for it to finish.
5. Check that your backup appears in the list. This is your copy of the save
   from before installing the editor. Keep it.
6. Exit JKSV, then fully turn off Switch 1 again as described in step 3.

JKSV's buttons are shown at the bottom of its screen. In the current version,
**A** on **New** creates a backup; **Y** restores a highlighted backup.
[JKSV's controls](https://github.com/J-D-K/JKSV/blob/rewrite/source/appstates/BackupMenuState.cpp).

## 5. Copy the editor ZIP into the backup directory

1. Move the SD card back to your computer.
2. Open the card's **JKSV** folder. Inside it, find the folder for **Seedsow
   Lullaby**. Its exact name can vary.
3. Open that game's folder. You should see the backup you just made, named
   **Before Lua Editor** or the automatic name you noted. It may be a ZIP or
   a folder.
4. Copy **Seedsow-Lua-Editor-Save.zip** into this same game folder, alongside
   your backup. Do not put it inside the backup itself.

   ```text
   SD card/
     JKSV/
       Seedsow Lullaby .../           (use the folder JKSV created)
         Before Lua Editor.zip       (or a folder with this name)
         Seedsow-Lua-Editor-Save.zip  (the downloaded file)
   ```

5. Leave your original backup in place. Eject the card in Windows, return it to
   the powered-off Switch 1, and boot back into that same system environment.

If you cannot find the game folder, search the SD card for the name of your
new backup. The folder containing that backup is where the downloaded ZIP
should go.

## 6. Restore the editor on Switch 1

**This replaces the current Seedsow save for the selected user.** Confirm you
have the backup from step 4 before continuing.

1. Open the homebrew menu and **JKSV** again.
2. Select the same user and **Seedsow demo**.
3. Highlight **Seedsow-Lua-Editor-Save.zip** in its backup list. JKSV may display
   the name without the `.zip` ending.
4. Press **Y** for **Restore**, then follow the on-screen confirmation. If it
   asks you to hold a button, keep holding it until the confirmation completes.
5. Wait until the restore finishes. Exit JKSV.
6. Start Seedsow as the same user. Open **Load** and select **slot 1**, whose
   title includes **LUA EDITOR**.
7. Confirm that the editor screen appears. Its first launch registers the
   editor and backup entries. Close the game normally before transferring.

The starter contains recovery slots 1-3 and examples in slots 4 and 5. It has
portable JKSV restore metadata with personal account fields blanked, rather
than someone else's account details.

## 7. Move the demo save to Switch 2

Keep the consoles near each other, with both connected to the internet and
the same Nintendo Account linked to the intended save user on each console.
The source must be in the environment where you restored the save, with Nintendo
servers reachable; an isolated emuMMC with blocked servers cannot complete this.

1. On **Switch 1**, open **System Settings > Data Management > Transfer Your
   Save Data > Send Save Data to Another Console**. Select the intended user
   and the **Seedsow demo** save.
2. On **Switch 2**, open **System Settings > Data Management > Transfer Your
   Save Data > Receive Save Data**.
3. Check the user and game on the screens, then finish the transfer. If asked
   to overwrite an existing target save, only continue once anything you want
   to keep has been preserved.

This **moves** the selected save off Switch 1. It is Nintendo's individual-game
save transfer, not the full system transfer used when setting up a new console.
Availability depends on the installed software and current transfer support.
[Official transfer instructions](https://www.nintendo.com/en-gb/Support/Troubleshooting/How-to-Transfer-Your-Save-Data-To-a-Nearby-Console-1549113.html).

## 8. Check Switch 2, then stop here if you only want to future-proof

1. On Switch 2, start the same demo as the receiving user.
2. Open **Load** and choose **slot 1**. The editor should appear.
3. Fully close the game with **HOME > X > Close**. Start it again and load
   **slot 1** once more. This checks that the editor remains installed.
4. Optionally load **slot 5** for the included blue animation. Press **B** to
   return to the editor.

> **You're set up. Everything else can wait.** You do not need the Pi uploader,
> Python, coding knowledge or an editor update right now. Keep the game and its
> save, retain recovery slots 1-3, and keep your backup.

Ordinary editing, saving and running now happen on Switch 2 **without a Nintendo
connection**. The optional Windows/Pi upload path is only a convenience, not a
requirement for running Lua. You do not need
Switch 1 for each new program. You can learn the
[console editor controls](07-console-editor.md), add
[optional PC uploads](02-pi-setup.md), or install
[compatible later updates](04-updates-recovery.md) whenever you want.
