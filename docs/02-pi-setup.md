# Optional: set up a Pi for Windows uploads

The working hardware path uses a Pi as a Bluetooth Pro Controller. Once set up,
the Windows app handles pairing, calibration, sending and manual controller
buttons. You do not need an open Pi desktop.

Windows and Raspberry Pi describe the implemented uploader, not requirements for
running Lua. After the initial Nintendo save transfer, this path needs only the
PC/Pi LAN connection and console Bluetooth; it does not contact Nintendo servers.

## Before you start

This is optional. Install and verify the console editor first; you can keep
using it with the controller or a wired keyboard for as long as you want.
A Pi is useful when you want to send larger programs and files from Windows.
If you already have a configured bridge, import its private connection JSON
in the app rather than reinstalling the service.

## New Pi installation

Use a Pi running Raspberry Pi OS or another compatible Debian Linux with
Bluetooth, `apt`, and `systemd`. Enable SSH and connect it to the same LAN as
Windows. The original trial used a Pi 3B's built-in Bluetooth adapter.

1. Copy this entire source folder to the Pi. For example, from PowerShell in
   the folder containing this project:

   ```powershell
   scp -r seedsow-lua-editor YOUR_USER@raspberrypi.local:~/
   ssh YOUR_USER@raspberrypi.local
   ```

   Replace `YOUR_USER` and the hostname with your Pi account and address. Use
   the Pi's IP address if `.local` names do not resolve.

2. In the Pi terminal, install the service:

   ```sh
   cd ~/seedsow-lua-editor
   sudo sh pi/install.sh
   ```

   The installer gets the required Debian packages, downloads the pinned NXBT
   source revision, applies the controller compatibility fixes, and installs the bridge in
   `/opt/seedsow-input`. The service starts at boot. It uses root for BlueZ
   controller setup; installing can restart Bluetooth and disconnect other
   Bluetooth devices using the Pi.

3. Export a private Windows connection file:

   ```sh
   python3 pi/export_connection.py --output ~/seedsow-connection.json
   ```

   If needed, add `--host YOUR_PI_IP` to use an explicit address. The export
   contains the generated bridge token. The installer keeps an existing token
   on subsequent runs.

4. In a **Windows** PowerShell window, copy that file back:

   ```powershell
   scp YOUR_USER@raspberrypi.local:~/seedsow-connection.json .
   ```

5. Open **START WINDOWS.cmd**. On **Connect & calibrate**, select **Import
   connection file…** and choose the copied JSON. The app saves the connection
   under `%LOCALAPPDATA%\SeedsowLuaEditor\settings.json`.
6. Click **Save & test connection**. The app should report that the Pi is reachable.

Keep connection files private. The bridge uses authenticated HTTP on LAN port
**39391**; it does not use TLS. Use a trusted LAN and keep the port off the
public internet. No SSH password is stored by the Windows app.

## Pair as Player 1

1. For the initial test, turn airplane mode **off** on the console. Later you
   can use airplane mode with its Bluetooth controller exception enabled.
2. Put other nearby paired consoles to sleep so the Pi connects to the intended one.
3. On the target console, open **Controllers → Change Grip/Order**.
4. In the PC app, click **Pair controller**.
5. Register the Pi controller as **Player 1**. The PC connection line reports
   the player number when available. Use Change Grip/Order again if another
   controller is occupying Player 1.
6. Return to Seedsow. The **Controller** tab in Windows provides D-pad, face
   and shoulder buttons if you need them to navigate.

## Calibrate once

1. Load console **slot 2: PC INPUT / CALIBRATE**.
2. On a fresh installation, it should say **INPUT CALIBRATION**, waiting for
   **physical A**. If it already says **PC INPUT: 0 / ? bytes**, the saved
   calibration is loaded and you can skip to [sending](03-send-files.md).
3. In Windows, tick **Console is on INPUT CALIBRATION, waiting for physical A**.
4. Click **Calibrate controller** and release every other controller.
5. Wait about 18 seconds. Windows sends A, B, X, Y, L, R with holds and releases.
6. Success on the console is **PC INPUT: 0 / ? bytes**. The editor may still display a
   stale “hold physical R” heading above that line; the zero-count receiver
   status means calibration is complete.

The console stores its measured mapping. Loading slot 2 later arms the receiver
directly. See [Troubleshooting](05-troubleshooting.md) if calibration stalls.

## Service commands

Run these on the Pi, or through an SSH session:

```sh
sudo systemctl status seedsow-input --no-pager
sudo journalctl -u seedsow-input -n 60 --no-pager
sudo systemctl restart seedsow-input
sudo systemctl stop seedsow-input
sudo poweroff
```

Restarting the service interrupts a transfer. After a stop or restart, leave the
console receiver with L and load slot 2 again before a fresh upload.
