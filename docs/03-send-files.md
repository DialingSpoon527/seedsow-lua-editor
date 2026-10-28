# Optional: send files from Windows

This guide is for the optional Pi upload setup. The console editor also works
without it; see [manual editing](07-console-editor.md).

Complete [console installation](01-console-install.md) and
[Pi setup/calibration](02-pi-setup.md) once. Later uploads use the Windows app
and console slot 2.

## First proof

1. Open **START WINDOWS.cmd**. Confirm that the Pi is reachable and its
   controller is connected as **Player 1**.
2. On the console, load **slot 2**. Confirm **PC INPUT: 0 / ? bytes**.
3. In Windows, select **Optional: send files**, then **New example**.
4. Keep **Lua launch slot** selected and choose a free user slot, for example
   **20**. Publishing replaces the destination slot and a file with the chosen
   filename; use a fresh filename and slot if you want to retain the old program.
5. Tick **Console slot 2 is armed and shows PC INPUT: 0 / ? bytes**.
6. Click **Send & save**. Leave console controls released while it sends.
7. Wait for the console to say **PC FILE SAVED**, with the expected filename,
   byte count and **SLOT 20**. Windows “input sent” only describes the Pi;
   there is no console-to-PC acknowledgement channel.
8. Hold **L** to leave the console receiver. You can use **Hold L / leave
   receiver** on the PC app's Controller tab.
9. Return to the game's load menu and load **slot 20**. The blue proof screen
   should show the same **PC-… token** displayed in the Windows app, a changing
   clock, and a moving white bar.
10. Fully close and reopen Seedsow, then load slot 20 again to check persistence.

The proof is generated in the PC editor. It is distinct from the built-in blue
example that may already be present in console slot 5.

## Your own Lua

1. Click **Open file…** and select a `.lua` file, or edit the text in the app.
2. Choose a plain save filename: up to **64 ASCII** letters, digits, `_`, `-`
   and `.`. The first character must be a letter, digit or underscore.
3. Select **Lua launch slot** and an intended slot from **4–120**.
4. Arm console slot 2 at zero, tick the ready box and **Send & save**.
5. After **PC FILE SAVED**, hold L and load your destination slot.

The console validates the checksum before writing the received file. Previous
readable contents are backed up as `.bak`, and saves are checked by readback.
Use **Save on PC…** to keep your local changes; editing the Windows buffer does
not automatically save your original PC file.

## Raw data

1. Open the file and choose **Raw file**. Binary previews are read-only and
   display only the beginning of the file; transmission uses all original bytes.
2. Enter the destination filename. Protected editor filenames are rejected.
3. Arm slot 2 at zero and send.
4. Confirm **PC FILE SAVED**. No Lua launch slot is created in Raw file mode.

Raw files are stored literally. Native executable bytes remain data, and the
editor does not repair the format of a raw save file you write. The limit is
**1 MiB per file**, but controller transfer time grows with each byte.

## Speed, cancellation and another upload

- Start with **Normal**. Try **Slow** if packets fail. **Fast** has less timing
  margin and needs testing with your hardware.
- A tiny example takes around a minute. A 5.6 KB editor update can take
  roughly 25–36 minutes. Progress and remaining time are estimates.
- **Stop sending** stops Pi transmission. Hold **L** on the console to leave
  the receiver. Loading slot 2 again gives a fresh zero count.
- Both success and error stay on the console until L, so trailing inputs cannot
  operate editor buttons. Never begin a new packet at a partial byte count.

For editor updates, follow [Updates and recovery](04-updates-recovery.md).
