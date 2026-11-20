# Pico 2 W — no adapter needed

Use a **Raspberry Pi Pico 2 W and a USB data cable**. No UART adapter, jumper
wires, headers, or second Switch is needed. The Pico stores the uploader and
sends it as controller input. Your PC prepares its firmware once, then sends
Artemis over the local network after the uploader is saved.

**Experimental: compiled and checked offline. Physical button input, calibration
and a complete console transfer still need hardware testing.** Keep your working
editor and its original slots. The Pico cannot see the console screen.

## 1. Choose your settings

1. Extract this installer into an ordinary folder on your computer; do not run it inside a ZIP.
2. Install Python 3.10 or newer. In PowerShell, `py --version` should report Python 3.
3. Confirm the console's Lua Editor works. Keep slots 1–3 unchanged.
4. Check **two different unused slots**, from 4–120: one for the uploader and one for Artemis. Write them down. Do not assume 20/21 are empty.
5. Confirm the filename `artemis-uploader.lua` is unused. A custom-filename command is below if needed.
6. On the PC, run `ipconfig` and note the **PC's LAN IPv4 address** for the network shared with the console.

## 2. Create your firmware on the PC

1. Double-click **SETUP_PICO2W_STANDALONE.cmd** in the installer folder.
2. Enter your PC address, TCP port (for example `39000`), empty Artemis slot, and different empty uploader slot.
3. Check the slots reported beside **Created**.
4. Open `build/pico2w-standalone/`. Find **pico2w-standalone-CONFIGURED.uf2** and keep its accompanying `config.json`.

No compiler or Pico SDK is needed for these steps. The tool places your uploader
in a reserved area of the template firmware. Generated files contain your PC
address; keep them private. Output folders must be empty; preserve earlier output
by moving it aside or selecting another folder.

For a custom filename/output folder, open PowerShell in the installer folder and
replace all example settings with your own:

```powershell
py tools/make_pico2w_standalone.py --ip 192.168.1.2 --port 39000 --slot 20 --uploader-slot 21 --name new-uploader.lua --output-dir build/my-pico
```

On macOS/Linux use `python3` instead of `py` and run the script directly.

## 3. Flash the Pico using its USB cable

1. Disconnect the Pico from the console. Keep its previous UF2 if you want to restore it later.
2. Hold **BOOTSEL on the Pico** while plugging it into the PC with a USB data cable.
3. Release BOOTSEL. Open **File Explorer → This PC → RP2350**.
4. Copy **pico2w-standalone-CONFIGURED.uf2** onto that drive itself.
5. Wait for the drive to disappear as the Pico restarts. Unplug it from the PC.

Use your **CONFIGURED** file from `build/`, not the blank **TEMPLATE** file in
`firmware/`. The blank template cannot upload a file. This build targets the
**Raspberry Pi Pico 2 W**, not the original Pico or arbitrary RP2350 boards.

## 4. Test the controller on the console

1. With your ordinary controller, enable **Pro Controller Wired Communication** in the console's controller settings.
2. Connect the Pico to the console dock by USB, with BOOTSEL released.
3. Wait **five seconds**. Plugging in sends no button presses.
4. Open **Test Controller Buttons** with your ordinary controller.
5. Briefly tap BOOTSEL on the Pico, then release. It sends **L+R**, releases them, then sends **A**. Check those buttons appear on the console.
6. If nothing appears, stop and check the USB data cable, firmware and wired-controller setting. A dark Pico LED is normal.
7. Return to **Change Grip/Order**. A short BOOTSEL tap supplies L+R and then A to register the Pico. Arrange it as **Player 1**; use your ordinary controller to navigate as needed.

## 5. Calibrate if the editor asks

1. Open Seedsow with the profile containing your working Lua Editor.
2. Load **slot 2 — PC INPUT / CALIBRATE**.
3. If it already displays **PC INPUT: 0 / ? bytes**, skip calibration and continue to step 6.
4. If it displays **INPUT CALIBRATION**, waiting for physical A, hold BOOTSEL for **two seconds**, then release.
5. Leave all other controls alone. The Pico sends A, B, X, Y, L and R with pauses; allow about **18 seconds**.
6. Confirm **PC INPUT: 0 / ? bytes**. If it does not reach this state, keep the error text and stop before sending a file.

## 6. Send the uploader

1. Confirm the configured filename and both slots are still unused.
2. Keep the console receiver at **PC INPUT: 0 / ? bytes**.
3. Hold BOOTSEL for **five seconds**, then release it. File input starts on release.
4. Leave the Pico connected and other controllers untouched. Allow at least the setup tool's estimate—about **37 minutes** for the compact uploader.
5. Watch the console receiver's progress. Elapsed time alone does not establish success.
6. Confirm **PC FILE SAVED**, the filename, source byte count and uploader slot. Compare them with `pico2w-standalone-settings.json` in your generated folder.
7. Unplug the Pico after the console confirms success. Hold L on your ordinary controller to leave the receiver.

There is only **one file-transfer start per power-on**. The firmware cannot tell
whether the console saved the file; the console's confirmation is required.

## 7. Install Artemis over the network

1. On the PC, double-click **START_PICO2W_STANDALONE_SENDER.cmd**. Wait for **Listening**.
2. For a custom output folder, use your own path instead:

   ```powershell
   py pc/send_alula.py --config build/my-pico/config.json --out build/my-pico/installer
   ```

3. Follow [Run the uploader](08-finish-installation.md#2-run-the-uploader-on-the-console): open your **uploader slot**, then use **RUN buffer**. The PC should report a connection.
4. Follow the installation-log checks before opening your separate Artemis slot.
5. Keep the PC address/port unchanged until installation finishes. If they change, generate and flash a new configured image before sending a replacement uploader.

## Cancel or retry

Press BOOTSEL during calibration or transfer to cancel. It releases the emulated
buttons and locks commands until unplugged. Unplugging immediately also stops
input. USB loss or stalled reporting aborts; there is no automatic retry/resume.

Use your ordinary controller to leave and reload the receiver. Inspect any file
or slot already saved before another attempt. Reconnect the Pico with BOOTSEL
released, wait five seconds, confirm a fresh receiver and deliberately start again.

| BOOTSEL action after the initial five-second wait | Result |
| --- | --- |
| Brief tap, under one second | L+R registration, then A button test |
| Hold about two seconds, then release | Calibration |
| Hold five seconds, then release | One uploader transfer |
| Press during calibration/transfer | Cancel and lock until unplugged |

Thresholds are under 1 second / 1–3.5 seconds / at least 3.5 seconds. Use the
distinct durations above, only on the intended console screen. Holding BOOTSEL
while plugging into the PC still enters the usual flashing mode.
