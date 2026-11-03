# First installation: use Alula's launcher save

If you have not installed the Seedsow Lua Editor, start with
[Alula's switch-artemis-launcher](https://github.com/alula/switch-artemis-launcher/).
This guide expands its JKSV and save-transfer steps for the **Seedsow Lullaby
demo**. The uploader is for an editor you already have.

## Before you begin

You need:

- A modded **Switch 1** with working Atmosphere/homebrew access, its microSD
  card and a way to copy files to that card.
- The **Seedsow Lullaby demo** installed on Switch 1 and Switch 2. Alula lists
  title ID `010042D022AEA000`. Its full-game support is not established; use the
  supported demo rather than the old editor's full-game instructions.
- A user on each console linked to the **same Nintendo Account**.
- Internet access on both consoles for Nintendo's save-transfer service.
- A computer to download and copy the save ZIP and JKSV.

**Firmware checkpoint:** the existing preparation instructions target **23.0.1**.
Before accepting a later system update, check the current guidance in
[Alula's project](https://github.com/alula/switch-artemis-launcher/). Nintendo's
transfer service can require a system update; a guide written for 23.0.1 does
not establish compatibility with later firmware. Check your Switch 1 CFW and
bootloader's firmware support as well.

Use **sysNAND/sysMMC**, the Switch 1's internal system storage, throughout.
Download, account setup and transfer happen in **stock sysMMC**. Boot **CFW
sysMMC** to use JKSV, then return to stock. An emuNAND/emuMMC has separate saves
and is not the source save used by stock mode.

Nearby save transfer works with the **demo on both consoles** and requires no
full-game purchase or Nintendo Switch Online membership. It still connects to
Nintendo's servers. A demo save cannot be transferred into the full game.

## 1. Prepare the demo and its save

1. Install the same supported demo on both consoles. On each, use the intended
   save user linked to the matching Nintendo Account. The account that
   downloaded the demo can be different, provided your save user can launch it.
2. On **Switch 1 in stock sysMMC**, launch the demo under that user.
3. Choose **New Game**, hold **R** through the opening until normal dialogue,
   release R, then press **ZL** to open the save menu.
4. Save into a slot and wait for saving to finish. This creates the save JKSV
   needs; merely opening the title screen does not.
5. Press **HOME**, highlight the game, press **X**, and choose **Close**.

## 2. Download the two files

1. Open [Alula's releases](https://github.com/alula/switch-artemis-launcher/releases).
   Expand **Assets** for the release and download **`seedsow_save.zip`**.
   Choose the Seedsow asset, rather than `nora2_save.zip` or GitHub's Source code
   downloads. Leave the save as a ZIP.
2. Download [JKSV.nro](https://github.com/J-D-K/JKSV/releases/latest/download/JKSV.nro)
   if JKSV is not already installed on Switch 1.

Alula maintains the launcher and its release downloads. Follow any new
game/version requirements included with the release you choose.

## 3. Install JKSV and make a backup

1. Fully power off Switch 1: hold its power button, then **Power Options > Turn
   Off**. Remove the microSD card and connect it to your computer.
2. If needed, copy **JKSV.nro** into the card's top-level **switch** folder:

   ```text
   SD card/
     switch/
       JKSV.nro
   ```

3. Eject the card, return it to Switch 1 and boot **CFW sysNAND/sysMMC**.
4. Open your homebrew menu and launch **JKSV**. Depending on your setup, the
   homebrew menu opens through Album or by holding R while launching a game.
5. Select the matching-account user, then the **Seedsow demo** entry.
6. Choose **New** to back up its current save. Name it **Before Artemis**, or
   note the automatic backup name. Wait for it to finish and keep this backup.
7. Exit JKSV and fully power off Switch 1 before removing its card again.

If the demo is missing from JKSV, check that you made an actual in-game save
under the selected user in step 1.

## 4. Copy and restore Alula's save

1. Put the microSD card back in your computer. Open **JKSV**, then the Seedsow
   game folder JKSV created. Find your **Before Artemis** backup there.
2. Copy the downloaded **seedsow_save.zip** alongside that backup:

   ```text
   SD card/
     JKSV/
       Seedsow Lullaby .../     (use the folder JKSV created)
         Before Artemis.zip    (or a backup folder)
         seedsow_save.zip
   ```

3. Eject the card, return it to Switch 1 and boot **CFW sysMMC**.
4. Open JKSV, select the same user and demo, and highlight **seedsow_save**.
5. Choose **Restore** (normally Y), then follow JKSV's confirmation prompt.
   **This replaces that user's existing game save.** Use the backup from step 3
   if you later need to restore what was there before.
6. Wait until restoration finishes, exit JKSV and power off Switch 1.
7. Boot back into **stock sysMMC**. The restored save is still in that same
   internal storage.

## 5. Transfer the save to Switch 2

Keep the game closed, place the consoles near each other and connect both to
the internet. Use the matching Nintendo Account users.

1. On **Switch 1**, open **System Settings > Data Management > Transfer Your
   Save Data > Send Save Data to Another Console**. Choose the intended user
   and the **Seedsow demo** save.
2. On **Switch 2**, open **System Settings > Data Management > Transfer Your
   Save Data > Receive Save Data**.
3. Check the user and game, then follow the transfer prompts. If Switch 2
   already has a save you want to keep, preserve it before confirming replacement.
4. Wait for the transfer to finish. Keep your Switch 1 JKSV backup separately.

This moves the selected save off Switch 1. It is the individual-game transfer,
not a full console system transfer. See
[Nintendo's nearby-transfer instructions](https://www.nintendo.com/en-gb/Support/Troubleshooting/How-to-Transfer-Your-Save-Data-To-a-Nearby-Console-1549113.html).

The launcher save is now installed on Switch 2. If you are preparing for later,
this is the stopping point.

## Start using the launcher

When you want to use it, open the demo under the receiving user and follow
Alula's launcher screen. Press **Y** for the HTTP server. Connect the console
and computer to the same trusted LAN, find the console's IP under **System
Settings > Internet > Internet Settings > your connected network**, and open
`http://YOUR_SWITCH_IP:8080/status` on the computer, replacing `YOUR_SWITCH_IP`.

Continue with [using the HTTP server](02-existing-editor.md#5-use-the-launcher).

For later updates to this replacement save, use
[Alula's update instructions](https://github.com/alula/switch-artemis-launcher#updating)
and its unprefixed filenames. The `ax_` filenames in the existing-editor guide
belong to the existing-editor install route.
