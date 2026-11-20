# Method 2 — send the uploader with a Raspberry Pi

Use this method with a **full Raspberry Pi running Linux**, such as a Pi 3B. The Pi acts as a Bluetooth controller. Your computer tells it which inputs to send.

First finish [Prepare your computer and editor](02-existing-editor.md). You need the generated **build/TYPE_THIS_EXACT.lua** and your uploader slot number.

## 1. Get the companion

1. On your computer, download [Seedsow PC Companion 0.1.3](https://github.com/DialingSpoon527/seedsow-lua-editor/releases/download/v0.1.3/Seedsow-PC-Companion-and-Source-0.1.3.zip).
2. Extract the ZIP into a separate folder.
3. Open its inner **seedsow-lua-editor** folder, containing **pc**, **pi**, and **START WINDOWS.cmd**. Call this the **companion folder**.
4. Keep both folders available. The installer folder contains your newly generated uploader. The companion folder contains the controller-transfer app.

If your Pi bridge already works, you can use its existing private connection file with the companion. To apply the compatibility fixes described here, update the Pi service using step 2 first.

## 2. Install the bridge on the Pi

You need a Pi with Bluetooth, a Debian-based Linux installation with `apt` and `systemd`, and SSH enabled. Connect it to your local network. Write down its IP address and the username you created when setting it up.

1. Open a terminal on your computer in the **installer folder**, containing this guide’s `pi` and `pc` folders. The updated Pi service comes from this installer folder. The separate companion folder supplies the desktop app.
2. Create a folder on the Pi. Replace `PI_USER` and `PI_IP` with your Pi account name and address.

   ```sh
   ssh PI_USER@PI_IP "mkdir -p ~/seedsow-artemis-installer"
   ```

3. Copy the updated Pi service and its protocol files to that folder.

   ```sh
   scp -r pi pc PI_USER@PI_IP:~/seedsow-artemis-installer/
   ```

4. If SSH asks, confirm the host is your Pi and enter its account password. The password prompt may show no characters as you type. Open a Pi terminal session.

   ```sh
   ssh PI_USER@PI_IP
   ```

5. In that Pi session, run these commands one at a time.

   ```sh
   cd ~/seedsow-artemis-installer
   sudo sh pi/install.sh
   ```

6. Wait until installation finishes. It installs the Bluetooth controller service and may restart Bluetooth, disconnecting other Bluetooth devices using the Pi.
7. Check that the service is running.

   ```sh
   sudo systemctl status seedsow-input --no-pager
   ```

Look for **active (running)**. If it failed, keep the error and use the Pi section in [Troubleshooting](05-troubleshooting.md). The updated service disables BlueZ’s Input plugin temporarily while it is running. Other explicitly configured plugin settings are retained. Bluetooth keyboards and mice using that Pi may be unavailable during this time. A custom or stale wildcard override is reported for inspection instead of overwritten. Installation on each Pi OS and Bluetooth adapter still needs verification.

## 3. Copy the Pi’s connection settings to the computer

1. In the Pi session, export the settings. Replace `PI_IP` with the Pi address.

   ```sh
   python3 pi/export_connection.py --host PI_IP --output ~/seedsow-connection.json
   ```

2. Leave that window open. Open a **second terminal on your computer** in the companion folder.
3. Copy the settings back to the computer.

   ```sh
   scp PI_USER@PI_IP:~/seedsow-connection.json .
   ```

4. Look for **seedsow-connection.json** in the companion folder. It contains a private token. Keep it private.

## 4. Open the companion and connect

1. On Windows, double-click **START WINDOWS.cmd** in the companion folder. On macOS/Linux, open a terminal there and run `python3 pc/app.py`.
2. If the window cannot start because Tk is missing, install Tk for that Python. The previously reported Mac setup used `brew install python-tk`. Debian-based desktop Linux commonly uses `sudo apt install python3-tk`.
3. Open the companion’s **Optional: connect Pi** tab.
4. Click **Import connection file…** and choose **seedsow-connection.json**.
5. Click **Save & test connection**.
6. Wait for confirmation that the Pi is reachable. This checks the computer-to-Pi connection.

## 5. Connect the Pi controller to the console

1. On the console HOME Menu, open **Controllers → Change Grip/Order**.
2. In the companion, click **Pair controller**.
3. Wait for the controller to appear. Make it **Player 1**.
4. Confirm and leave the pairing menu. Check that the Pi still sends ordinary button input after leaving this menu.
5. If airplane mode is enabled, allow Bluetooth/controller communication. The console also needs Wi-Fi or Ethernet for the later network installation.

If pairing fails or input stops, collect the service log on the Pi with `sudo journalctl -u seedsow-input -n 60 --no-pager`. A Bluetooth error here is separate from `send_alula.py` waiting for a network connection later.

## 6. Calibrate the editor receiver

1. Return to Seedsow and load **slot 2 — PC INPUT / CALIBRATE**.
2. Read the screen. If it already says **PC INPUT: 0 / ? bytes**, continue to step 7.
3. If it says **INPUT CALIBRATION** and is waiting for **physical A**, tick the matching confirmation box in the companion.
4. Click **Calibrate controller**.
5. Release all other controls and wait about 18 seconds.
6. Continue when the console says **PC INPUT: 0 / ? bytes**. A stale heading above that message may remain on screen.

## 7. Send the generated file

1. In the companion, open **Optional: send files**.
2. Click **Open file…**.
3. Select **TYPE_THIS_EXACT.lua** from the **installer folder’s build directory**.
4. Choose **Lua launch slot** and enter your **uploader slot**.
5. Enter a new filename such as `artemis-uploader.lua`. Check that both the filename and uploader slot are free.
6. Choose **Normal** speed.
7. Check that the console still shows **PC INPUT: 0 / ? bytes**, then tick the ready confirmation.
8. Click **Send & save**. Let it finish without touching other controls.
9. Wait for **PC FILE SAVED on the console**. Check the filename, source byte count, and uploader slot. The PC progress bar alone does not confirm that the save succeeded.
10. Hold **L** to leave the receiver. The companion also has **Hold L / leave receiver**.

If transmission fails, stop the companion, leave the receiver with L, and load slot 2 again. Check that it starts at zero before a fresh attempt. Try **Slow** speed for more timing margin.

Continue with [Install and open Artemis](08-finish-installation.md).
