# Beginner guide: get the editor save onto Switch 2

> [!IMPORTANT]
> **Firmware checkpoint — 2026-10-27:** this preparation guide targets
> **23.0.1 on both Switch 1 and Switch 2**, while it is the latest firmware.
> Nintendo requires current firmware for the official save transfer.
> **If a newer firmware has been released, stop before updating and get updated
> project guidance.** A later update may change the future filesystem (FS)
> preparation path even if this Lua editor continues to run.
> On Switch 1, check that your CFW and bootloader support 23.0.1 before updating.
>
> **Accounts:** add or use a user on each console linked online to the **same
> Nintendo Account**. These are the users whose game save will be transferred.

Version sources, checked 2026-10-27:
[Switch 1](https://www.nintendo.com/au/support/articles/system-update-information-for-nintendo-switch/),
[Switch 2](https://www.nintendo.com/au/support/articles/system-update-information-for-nintendo-switch-2/).
See [Nintendo's save-transfer requirements](https://www.nintendo.com/en-gb/Support/Troubleshooting/How-to-Transfer-Your-Save-Data-To-a-Nearby-Console-1549113.html).

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

Choose a transfer route before downloading the game:

| Route | Switch 1 source | Switch 2 target | Nintendo Switch Online membership |
| --- | --- | --- | --- |
| **Nearby/local save transfer — beginner path below** | Demo | Same demo | **Not required** |
| **NSO Save Data Cloud — reported alternative** | Demo or full game | **Full game required** | **Required** |

**You do not need the full game for nearby/local transfer.** The demo works on
both consoles. **Local does not mean offline:** both consoles still need an
internet connection to Nintendo's servers and matching Nintendo Account users.
The cloud route also needs Nintendo connectivity and the same account.

The demo/full-game cloud route was reported by users on 2026-10-27; the maintainer
has not independently reproduced it. See [step 7](#7-transfer-the-save-to-switch-2)
for both methods and [compatibility evidence](compatibility.md#transfer-routes)
for the limits of that report.

- Your hacked Switch 1, including its microSD card and working homebrew menu.
- Your Switch 2.
- A computer and a way to read the Switch 1's microSD card on it. A microSD card
  reader or SD adapter is enough. The file-copy steps below use Windows names.
- For the nearby route, the same Seedsow Lullaby edition installed on both consoles. The tested
  reference used in this guide is **demo 1.0.0 obtained from the US eShop**.
  There are also user-reported working cases for the **Japanese demo**,
  **EU demo** and **US full game**; see [compatibility notes](compatibility.md)
  for the distinction between reference testing and community reports.
- The same Nintendo Account linked to the user you will use on each console.
- Internet access on both consoles for the save-transfer step.

The matching account is for the **save users and Nintendo's transfer process**.
It is not inherently required that this account downloaded the demo. Each selected
user must be able to launch the installed software.

### Check the source setup before restoring

**Use sysNAND/sysMMC, not emuNAND/emuMMC, for this installation.** All Switch 1
stages use the console's internal system storage. **Stock is also sysNAND**;
you only need to boot **CFW on sysNAND to use JKSV**. Download the game, link the
account, check the editor and transfer or upload the save in stock mode.
The boot mode changes while the underlying saves stay the same:

| Stage on Switch 1 | Boot mode |
| --- | --- |
| Download the demo, link the account and make the first save | **Stock sysMMC**, without CFW |
| Back up and restore with JKSV | **CFW sysMMC**, on that same internal storage |
| Check the editor, transfer locally or upload an NSO cloud backup | **Stock sysMMC**, without CFW |

An **emuNAND/emuMMC** is a separate system environment, usually on the SD card,
with separate saves. Restoring into emuMMC does not put the editor into the
stock sysNAND save you will transfer. Your bootloader's profile names may differ;
choose **CFW sysNAND/sysMMC** for JKSV, then return to **stock sysNAND/sysMMC**.
CFW on sysNAND is not ban-proof; an unbanned console is not a guarantee against
a future ban.

Both consoles need Nintendo connectivity and account verification for the initial
transfer. **Blocking Nintendo servers beforehand can prevent it.** Follow the
firmware checkpoint above before accepting an update. This project cannot
guarantee ongoing transfer availability. After installation, the editor runs without Nintendo
connectivity. See [Nintendo's requirements](https://www.nintendo.com/sg/support/switch/secondary/transfer.html)
and [compatibility notes](compatibility.md).

If you already installed this editor, keep your existing save. Do not restore
the starter over programs you want to keep.

## 1. Get the demo on both consoles

These steps follow the nearby demo-to-demo route. For the optional **NSO cloud
route**, install the **full game on Switch 2** instead; Switch 1 can use the demo
or full game. If using the full game on Switch 1, use that game's own save and
JKSV backup entry throughout steps 1–6. Check the [compatibility notes](compatibility.md)
before restoring to another edition; the prepared ZIP retains the reference
demo's metadata. A cloud-transfer report does not change that restore target.

### 1.A — Get the demo on Switch 2

1. On Switch 2, make sure you can open the Seedsow Lullaby **demo**.
   If needed, obtain it through Nintendo eShop using an account with access.
   The download account need not be the user whose save will be transferred.
2. Add or use the intended save user and link it online to the same Nintendo
   Account you will use for that user's save on Switch 1.
3. Check that this user can open the demo, then close it.

### 1.B — Get the demo and make the first save on Switch 1

1. Boot Switch 1 into **stock sysNAND/sysMMC, without CFW**.
2. Download the same demo edition as on Switch 2 if needed. Highlight it on HOME
   and press **+** to see its version. This project
   tested **1.0.0 from the US eShop**. Working cases have also been reported for
   the **Japanese demo**, **EU demo** and **US full game**, without exact version
   or feature details. These reports have not been independently reproduced by
   the maintainer. This guide follows the demo reference workflow.
3. Add or use the intended save user and link it online to the same Nintendo
   Account used for the receiving user on Switch 2.
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

You only need the two files above for the initial installation.
**Seedsow-PC-Companion-and-Source-VERSION.zip** is the optional computer app and
developer tools; extract that on a computer if you need it later. Older releases
call it `seedsow-lua-editor-VERSION.zip`. GitHub's **Source code** downloads are
also developer files. The file you restore with JKSV is the **Switch save ZIP**.

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

You have installed JKSV. You have not restored the editor save yet.

## 4. Open JKSV and back up the demo

0. Boot Switch 1 into **CFW sysNAND/sysMMC**. This uses the same internal storage
   as step 1.B, with CFW loaded so homebrew can run. **JKSV cannot run in stock
   mode.** Do not switch to an emuMMC that has a separate save.

If the demo does not appear in JKSV, go back to step 1.B and make the first
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
   the powered-off Switch 1, and boot back into **CFW sysNAND/sysMMC** for JKSV.

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
5. Wait until the restore finishes. Exit JKSV and fully turn off Switch 1.
6. Boot back into **stock sysNAND/sysMMC, without CFW**. The restored save is
   still on that same internal storage. Start Seedsow as the same user. Open
   **Load** and select **slot 1**, whose
   title includes **LUA EDITOR**.
7. Confirm that the editor screen appears. Its first launch registers the
   editor and backup entries. Close the game normally before transferring.

The starter contains recovery slots 1-3 and examples in slots 4 and 5. It has
portable JKSV restore metadata with personal account fields blanked, rather
than someone else's account details.

## 7. Transfer the save to Switch 2

Choose **one** method below. Both use Nintendo's services and the same Nintendo
Account for the save user on each console. Return Switch 1 to **stock sysMMC**
after the JKSV restore and editor check in step 6.

### 7.A — Nearby/local transfer: demo on both consoles

**No full-game purchase or NSO membership is required.** This is the beginner
path used throughout the guide. It still requires internet access to Nintendo's
servers on both consoles.

Keep the consoles near each other, with both connected to the internet and
the same Nintendo Account linked to the intended save user on each console.
Switch 1 should now be in **stock sysNAND/sysMMC**, using the internal save that
JKSV restored under CFW. Nintendo servers must be reachable.

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

### 7.B — NSO Save Data Cloud: full game on Switch 2

**Reported working:** upload the editor save from either the **demo or full game
on Switch 1**, then download it for the **full game on Switch 2**. The receiving
Switch 2 must have the full game for this route; the demo alone is insufficient.
This is a community report, not a separate maintainer-reproduced test. Exact
regional/version combinations were not recorded.

You need an active **Nintendo Switch Online membership**, internet access and
the same Nintendo Account for the save user on both consoles. Keep the original
JKSV backup. Cloud uploads can replace an existing cloud backup, and downloads
replace the target game's save; preserve anything you want to keep first.

1. After checking the restored editor on Switch 1, fully close Seedsow.
2. On **Switch 1**, open **System Settings > Data Management > Save Data Cloud**.
   Select the intended user and the Seedsow entry containing the restored editor
   save, then choose **Back Up Save Data**. Wait for the upload to finish and
   check its backup time before proceeding.
3. On **Switch 2**, ensure the **full game** is installed and playable by the
   user linked to that same Nintendo Account. Close the game if it is open.
4. Open **System Settings > Data Management > Save Data Cloud**, select that
   user and the Seedsow full-game entry, then choose **Download Save Data**.
   Confirm that you are downloading the backup just uploaded from Switch 1.
5. Wait for the download to finish, then continue to step 8 using the **full
   game** on Switch 2.

Cloud backup copies the save through Nintendo's servers; it does not remove the
source save like the nearby transfer does. Nintendo documents the general
[backup](https://www.nintendo.com/en-gb/Support/Troubleshooting/How-to-Back-Up-Save-Data-on-Nintendo-Switch-2-and-Nintendo-Switch-1434307.html)
and [Switch 2 download](https://www.nintendo.com/en-gb/Support/Troubleshooting/How-to-Download-Save-Data-Cloud-Backups-on-Nintendo-Switch-2-2879088.html)
steps. The specific demo-to-full-game behavior comes from the community report.

## 8. Check Switch 2, then stop here if you only want to future-proof

1. On Switch 2, start Seedsow as the receiving user: the **demo** for the demo
   nearby-transfer route, or the **full game** for the NSO cloud route.
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
