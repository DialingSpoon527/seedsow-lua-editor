# Troubleshooting

Find the last message you actually see. Keep the full error text and the editor version when asking for help. The Pi/Pico controller transfer and the later network sender have different connections.

## Python or a command window will not open

1. Open a terminal in the extracted installer folder.
2. On Windows, run `py --version`. On macOS/Linux, run `python3 --version`.
3. Install Python 3.10 or newer if needed. Reopen the terminal afterward.
4. Run the script directly from that terminal so the error stays visible. If your Windows Python is called `python`, use that name instead of `py`.

## Setup says a slot is invalid

Both slots must be between **4 and 120**, and must be different. Check the editor and game load menu for occupied slots. The PC cannot see which slots contain your programs. Choose an uploader slot and a separate Artemis destination.

## Sender says “Run tools/make_sheet.py first”

1. Return to the installer folder containing `SETUP_WINDOWS.cmd`.
2. Run setup and check the four settings.
3. Look for **build/config.json**.
4. Run the sender from that same copy of the installer. If you deliberately generated files elsewhere, use `--config` followed by the actual config path.

Changing settings on the computer also requires updating the uploader saved on the console.

## Download or checksum failure

The sender expects the pinned **v1 seedsow_save.zip**. Check that you downloaded the Seedsow asset with that exact name, rather than Source code or a different game’s save. Keep the ZIP unchanged. Use the local-file command in [Install and open Artemis](08-finish-installation.md#if-the-download-fails). Preserve an unexpected download for inspection rather than bypassing verification.

## “Address already in use” or a bind error

1. Close older sender windows.
2. Check that the computer still has the IPv4 address you entered during setup.
3. If another program uses the chosen port, choose a free port, run setup again, and update the console’s uploader too.
4. Start the sender again and wait for **Listening**.

## PC stays on “Listening”

The sender opened its TCP listener but has accepted no connection.

1. Check that you ran **RUN buffer** from the saved uploader slot.
2. Check the first three settings in the console copy against your current computer IP, Artemis slot, and TCP port.
3. Check that the console has active Wi-Fi or Ethernet access to the computer’s LAN.
4. Avoid guest Wi-Fi or VPN routes that prevent direct device communication.
5. Allow Python’s incoming TCP connection through the computer firewall on your private network.

The native uploader has no connection/read timeout. If the game freezes, close it with **HOME → X → Close**. Check the settings, start the PC sender first, then make a fresh console attempt. Repeated Run presses will not fix a blocked call.

## PC printed “Switch connected” before failing

A connection reached the PC. Keep the complete PC error, check for an interrupted network or game crash, and reopen the editor to inspect `ax_install.log`. A sent-byte counter is not confirmation that the console installed the files.

## No matching installation-complete log

1. Fully close and reopen Seedsow, then load the ordinary editor.
2. Open `ax_install.log` using **File / new**, then **TEXT** mode.
3. Scroll to its end. Match both the Artemis slot and current PC sender’s run ID.
4. Keep any **ARTEMIS_INSTALL_FAILED** line. An older completed run does not confirm the new one.

An interrupted install can leave partial files. Inspect those errors before attempting further writes.

## “SLOT_IN_USE”, “SOURCE_IN_USE”, or “COLLISION ax_…”

The destination already has files. This can be an existing program or a partial install. Keep the log and your backup. Choose a different free destination only after understanding what is already there. A different slot cannot resolve a conflict in shared `ax_` launcher files.

## Pi is unreachable from the companion

1. Check that the Pi is powered and on the computer’s LAN.
2. Import the private connection JSON exported by that Pi.
3. Confirm its address and port **39391**.
4. On the Pi, run `sudo systemctl status seedsow-input --no-pager`.
5. Preserve service errors from `sudo journalctl -u seedsow-input -n 60 --no-pager`.

## Pi is reachable but controller pairing or input fails

1. Put the console in **Controllers → Change Grip/Order** and click **Pair controller**.
2. Make the Pi Player 1. Keep other nearby consoles asleep if the controller connects to the wrong one.
3. Check ordinary button input after leaving the pairing menu.
4. If input fails, keep the service log and run `bluetoothctl --version` on the Pi.

NXBT and NUXBT document conflicts where BlueZ’s Input plugin occupies the controller’s Bluetooth channels. A blanket version cutoff is not established here. The newer NUXBT fork also documents this conflict. Changing system Bluetooth configuration can disconnect Bluetooth keyboards and other devices using the Pi. Keep the specific error before changing services. [NXBT troubleshooting](https://github.com/Brikwerk/nxbt#troubleshooting) · [NUXBT troubleshooting](https://github.com/hannahbee91/nuxbt#troubleshooting)

The older 0.1.3 companion installs a private, pinned NXBT copy in `/opt/seedsow-input/vendor`. Installing NUXBT separately does not change the library that this service loads. The pinned NXBT constructor restarts BlueZ using `--compat --noplugin=*`, which disables all plugins. That behavior may conflict with other Bluetooth services required on the Pi. The older companion patches change D-Bus connection handling and input reporting, but leave this startup behavior in place. The updated Pi installer in this folder replaces that blanket behavior with an Input-plugin-only override. [Pinned NXBT startup](https://github.com/Brikwerk/nxbt/blob/ec4b800ad6c55de96bb6c7f9f84b5bdc59a4c975/nxbt/nxbt.py#L167) · [Pinned BlueZ configuration](https://github.com/Brikwerk/nxbt/blob/ec4b800ad6c55de96bb6c7f9f84b5bdc59a4c975/nxbt/bluez.py#L86)

NUXBT 3.3.8 documents Switch 2 bonding, discovery, and reconnect fixes tested by its contributor on a Pi 5. Its Bluetooth toggle code still uses `--noplugin=*`, so those fixes do not establish coexistence with other required services. Preserve the exact service error, Pi OS version, BlueZ version, and whether ordinary button input reaches the console when reporting this problem. [Switch 2 fixes](https://github.com/hannahbee91/nuxbt/pull/78) · [NUXBT Bluetooth configuration](https://github.com/hannahbee91/nuxbt/blob/main/nuxbt/bluez.py)

## Pi reports a custom or wildcard Bluetooth override

The updated service keeps custom overrides for inspection. Stop any old controller bridge first and run `systemctl cat bluetooth.service` on the Pi. Check which drop-in supplies the conflicting `ExecStart` or wildcard plugin flag. Keep a copy of that file before changing it. If the override belongs to another Bluetooth application, settle which application will control the adapter before starting the bridge. Starting or stopping this service can restart Bluetooth and disconnect the Pi’s Bluetooth devices.

## Pico serial errors or no button input

1. Confirm that the USB-to-UART adapter appears in the port list, and use its current port name.
2. Close other applications using that port.
3. Install `pyserial==3.5` in the same Python used for the sender.
4. Verify the pinned firmware, 3.3 V UART signal levels, crossed TX/RX wiring, and common ground against [the Pico guide](07-pico-upload.md).
5. Check Pro Controller Wired Communication and run the one-button test again.

An open COM port alone does not confirm that the board or console received any input. On Linux, a permission error may require the serial-device access group appropriate to your distribution. Reopen your login session after changing group membership.

## Pico HTTP endpoint or token error

Check the board address, HTTP port, and token in your private connection JSON. The firmware must implement level-preserving `/press` and `/release` as well as `/status`. A tap-only bridge is insufficient for file transfer.

## Calibration or controller transfer stalls

1. Stop the PC transfer. Wait for it to stop sending.
2. Confirm that buttons have released. Disconnect the controller if release could not be confirmed.
3. Use L to leave the receiver, then load slot 2 again.
4. If calibration is waiting for physical A, recalibrate. Otherwise check for **PC INPUT: 0 / ? bytes** before sending.
5. Use Slow speed on the Pi, or `--prepare 0.20 --hold 0.40` for the Pico.
6. Inspect any destination slot or filename that may already have been saved before a repeat attempt.

## Artemis slot missing or launcher server unreachable

After a matching completed log, restart Seedsow and load the ordinary editor once to register the new slot. Then select **Title screen → Load** and open your chosen Artemis slot. Its name may contain `ax_slot…lua`.

On the launcher screen, press Y. Use the **console’s** IP at `http://YOUR_SWITCH_IP:8080/status`. This is separate from the **computer’s** uploader IP and the controller bridge port. Preserve any error on the launcher screen. Closing the game stops the server.

For this installer’s recovery controls and `ax_` update filenames, see [Install and open Artemis](08-finish-installation.md#updates-and-recovery).
