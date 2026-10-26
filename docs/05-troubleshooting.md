# Troubleshooting

## The Windows app does not open

Install Python 3.10 or newer from python.org with Tcl/Tk and the Python launcher.
From the project folder, try `py -3 pc/app.py`. Any error remains visible in that
terminal. WSL is not needed. Keep the `pc`, `editor`, `examples`, `tools` and
`docs` folders together when extracting the release.

## Windows cannot reach the Pi

1. Check the Pi is powered on and Windows and Pi share the same LAN.
2. Try the Pi IP address in place of its `.local` hostname.
3. Confirm port **39391** in the app and `/etc/seedsow-input.json`.
4. On the Pi, run `sudo systemctl status seedsow-input --no-pager` and
   `sudo journalctl -u seedsow-input -n 60 --no-pager`.
5. If the app says the token was rejected, export/import the Pi connection file
   again. Do not post that file or the token in an issue.

The app's saved settings are at
`%LOCALAPPDATA%\SeedsowLuaEditor\settings.json`. They stay outside the source repo.

## The Pi will not pair or disconnects on returning to the game

1. Leave airplane mode off for the initial test. Controller Bluetooth must remain
   enabled after leaving the pairing screen.
2. Put other nearby consoles to sleep and open **Change Grip/Order** on the
   intended console before clicking **Pair controller**.
3. Make the Pi **Player 1**. Seedsow input from a different player may be ignored.
4. Use the pinned library and continuous-report fix installed by `pi/install.sh`.
   Pairing alone does not demonstrate that reports continue inside the game.
5. After restarting the bridge, pair again if needed, then re-arm console slot 2.

The Pi 3B's ordinary USB ports cannot present a USB keyboard to the console.
This release exposes the established controller path. A real wired keyboard
can still type into the game's text-entry dialog.

## Calibration stalls, or still says hold R

Verify Player 1 and start on **INPUT CALIBRATION / physical A** before clicking
Calibrate. Release other controls. If the bottom says **PC INPUT: 0 / ? bytes**,
calibration has completed even if the “hold R” heading remains.

Calibration writes `ssedit-input-report.txt` and `ssedit-controls.txt` in the
game's save. A backup exported after the test can provide those reports for
diagnosis. They are ordinary data, not files to type back into the editor.

## Upload stops at a few bytes or shows an error

Stop Windows transmission, hold L to leave the console receiver, then load
slot 2 and check **0 / ? bytes** before sending again. Try **Slow**. Leave all
other controls released during transmission. Errors are latched until L.

An incomplete packet times out after ten seconds without data edges once bytes
have arrived. Transfer results/errors are recorded in
`ssedit-transfer-report.txt` in the game's save. Windows completion is not
console acknowledgement; look for **PC FILE SAVED** on the console.

## I only want to install the downloaded save

Follow the [beginner guide](01-console-install.md). Restore the already-built
save ZIP with JKSV; do not open the custom builder. No clean autosave, developer
hashes or Python installation is required for that path.

## Nintendo's save transfer will not complete

Both intended save users must be linked to the same Nintendo Account, and both
consoles must reach Nintendo for the initial transfer. The account that downloaded
the demo need not be that user. Check that you restored into the same environment
you are trying to transfer from: sysMMC and emuMMC have separate saves. An isolated
emuMMC normally blocks Nintendo servers. A banned or blocked source cannot finish
this documented online route. SysNAND CFW is not ban-proof. See the
[setup prerequisites](01-console-install.md#check-the-source-setup-before-restoring).
The installed editor itself does not require Nintendo connectivity afterward.

## The optional custom-save builder rejects my backup

The downloaded installer does not use this builder. For custom builds, see
[compatible-save inputs and troubleshooting](06-development.md#troubleshooting-a-custom-build).

If you already have the editor installed, keep it. The new PC app accepts the existing
Pi service and does not require a new console save installation.

## A published slot or editor update does not run

Use a free slot from 4–120, verify the console's **PC FILE SAVED / SLOT …**, then
hold L and load that exact slot. To prove persistence, fully restart the game.
For side-editor updates, build from a backup containing the same editor base as the
console. Retain slots 1–3 and follow [recovery steps](04-updates-recovery.md).

## Useful details to include with a problem report

Include game version, console model, Pi model/OS, which step failed, the exact
console status, Pi player number, file byte count, speed, and any relevant report
file. Remove connection tokens and personal save information before sharing.
