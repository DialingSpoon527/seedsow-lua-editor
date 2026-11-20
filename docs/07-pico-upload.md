# Method 3 — send the uploader with a Pico

First complete [Prepare your computer and editor](02-existing-editor.md). Keep the generated **build/TYPE_THIS_EXACT.lua** and your uploader slot number ready.

Choose **A** for a wired RP2040 Pico, or **B** if you already have a Pico W serving the compatible controller HTTP interface. Both use `pc/send_controller.py` for a real file transfer to the editor’s existing receiver.

**This sender has offline tests. A complete Pico-to-console transfer still needs a hardware trial.** Verify button input before sending any file.

## A. Set up a wired Pico

### 1. Gather the hardware

- An original **RP2040 Raspberry Pi Pico**, with headers fitted so you can connect jumper wires. The pinned UF2 targets RP2040. Pico 2 uses a different chip and needs a board-specific build.
- A USB data cable from the Pico to the console dock.
- A **3.3 V logic USB-to-UART adapter** supporting **921600 baud**, plus jumper wires. The adapter connects to your computer.
- Python 3.10 or newer on your computer, already checked in the preparation guide.

The Pico uses its USB connection for the console. The separate UART adapter carries the computer’s controller inputs.

### 2. Install the board firmware

This route uses the UART build of **jyapayne/switch-pico**, pinned to revision `02ff001ca206997229766256af0d0a096e26fb39`. The firmware is downloaded separately. [Firmware source](https://github.com/jyapayne/switch-pico/tree/02ff001ca206997229766256af0d0a096e26fb39)

1. Download [switch-pico.uf2](https://raw.githubusercontent.com/jyapayne/switch-pico/02ff001ca206997229766256af0d0a096e26fb39/firmware/switch-pico.uf2) to your computer. Keep the filename ending in `.uf2`.
2. Check the download if possible. It should be **90,112 bytes**, with SHA-256 `09624715fe5e78261936e0853086a236a93d11c30268965ac35c7f0325435901`.
3. Unplug the Pico. Hold its **BOOTSEL** button while connecting it to the computer with a USB data cable, then release BOOTSEL.
4. Open the **RPI-RP2** drive that appears and copy `switch-pico.uf2` onto it.
5. Wait for the drive to disappear as the board restarts. Unplug it before wiring.

This replaces the firmware already on the board. Keep the previous firmware file if you want to flash it back later. The separate AIO/Bluetooth firmware uses a different input arrangement from this guide.

### 3. Wire the adapter

Disconnect power from both devices first. Check the adapter’s documentation and select **3.3 V signal levels** before connecting it.

| Pico connection | Adapter connection |
| --- | --- |
| **GP4**, physical pin **6**, TX | RX or RXD |
| **GP5**, physical pin **7**, RX | TX or TXD |
| **GND**, for example physical pin **8** | GND |

Leave the adapter’s **VCC/5V/3V3 power pin disconnected**. The console powers the Pico over USB. TX connects to RX in each direction. [Upstream wiring reference](https://github.com/jyapayne/switch-pico/blob/02ff001ca206997229766256af0d0a096e26fb39/README.md)

1. Plug the Pico’s USB cable into the console dock.
2. Plug the UART adapter into your computer.
3. Use your ordinary controller to enable **Pro Controller Wired Communication** in the console’s controller settings.
4. Find the adapter’s serial port. On Windows, open **Device Manager → Ports (COM & LPT)** and note its COM number, such as **COM5**. On macOS/Linux, the listing command below can show the path.

### 4. Install the serial package

Open a terminal in the installer folder as explained in the preparation guide. On Windows, run these one at a time.

```powershell
py -m pip install pyserial==3.5
py -m serial.tools.list_ports
```

On macOS/Linux, replace `py` with `python3`. Use the UART adapter’s port in the commands below. `COM5` is an example. On macOS, it may look like `/dev/cu.usbserial-…`. On Linux, it may look like `/dev/ttyUSB0`. Close other programs using the adapter.

### 5. Check the serial connection

```powershell
py pc/send_controller.py --serial-port COM5 status
```

Look for **UART adapter opened**. This confirms the PC can open the adapter. The next step checks whether input reaches the console.

### 6. Test one button

1. On Switch 2, use your ordinary controller to open **System Settings → Controllers & Accessories → Test Input Devices → Test Controller Buttons**. [Nintendo’s button-test instructions](https://en-americas-support.nintendo.com/app/answers/detail/a_id/68213/)
2. Run the command below from the computer.

   ```powershell
   py pc/send_controller.py --serial-port COM5 tap A --ready
   ```

3. Look for **A** in the console’s button tester.
4. If there is no input, check the firmware, UART port, power, and wiring. Do this before calibration or file transfer.
5. Return to **Controllers → Change Grip/Order** and make the Pico **Player 1** before opening the editor receiver.

### 7. Calibrate the editor

1. Open Seedsow under the profile containing your editor.
2. Load **slot 2 — PC INPUT / CALIBRATE**.
3. If it already says **PC INPUT: 0 / ? bytes**, go to step 8.
4. If it says **INPUT CALIBRATION**, waiting for physical A, run this command.

   ```powershell
   py pc/send_controller.py --serial-port COM5 calibrate --ready
   ```

5. Release all other controls and let the sequence finish. It sends A, B, X, Y, L, and R with pauses between them.
6. Continue only when the console displays **PC INPUT: 0 / ? bytes**. If calibration stalls, keep the screen text and check [Troubleshooting](05-troubleshooting.md).

### 8. Send the uploader

1. Check that your uploader slot and the filename `artemis-uploader.lua` are unused.
2. Keep the console receiver at **PC INPUT: 0 / ? bytes**.
3. Run this command, replacing **COM5** and **20** with your adapter port and **uploader slot**.

   ```powershell
   py pc/send_controller.py --serial-port COM5 send build/TYPE_THIS_EXACT.lua --slot 20 --name artemis-uploader.lua --ready
   ```

4. Allow the transfer to finish without touching other controls. The sender prints a minimum time estimate and byte progress. This can take tens of minutes.
5. Check the console for **PC FILE SAVED**, the source byte count, filename, and uploader slot. A computer-side success message alone does not prove the console saved the file.
6. Hold **L** to leave the receiver. If you need to use the Pico to do that, run `py pc/send_controller.py --serial-port COM5 tap L --ready` while that receiver is open.
7. Continue with [Install and open Artemis](08-finish-installation.md).

## B. Use an existing Pico W HTTP bridge

This option is for board firmware already providing **GET /status** and **POST /press** and **/release**. Press/release must preserve other held buttons. A bridge implementing only `/tap` cannot carry this editor’s clocked button data. The Seedsow FS package describes this interface but does not include the board firmware.

1. Connect your board as its firmware directs. Test ordinary A button input on the console first, then make it Player 1.
2. Copy **examples/pico-connection.example.json** to a new file called **pico-connection.json** in the installer folder.
3. Open that new file in a text editor. Replace `PICO_IP` with the board’s address. Set its actual HTTP port and token, if required, and save it. Keep the file private.
4. In a terminal in the installer folder, run `py pc/send_controller.py --connection pico-connection.json status`. On macOS/Linux, use `python3`.
5. Look for **Controller HTTP bridge answered**.
6. Load the editor’s slot 2. If it is waiting for calibration, run `py pc/send_controller.py --connection pico-connection.json calibrate --ready`.
7. Once the console says **PC INPUT: 0 / ? bytes**, run the command below with your unused **uploader slot**.

   ```powershell
   py pc/send_controller.py --connection pico-connection.json send build/TYPE_THIS_EXACT.lua --slot 20 --name artemis-uploader.lua --ready
   ```

8. Check **PC FILE SAVED** on the console, including byte count, filename, and slot. Hold L to exit the receiver.
9. Continue with [Install and open Artemis](08-finish-installation.md).

## If a transfer stops

Press **Ctrl+C** in the sender terminal. It attempts to release its buttons. If it cannot confirm release, disconnect the controller and use your ordinary controller to leave the receiver. For the pinned UART firmware, unplug the Pico from the console if an input stays held after a cable or PC failure.

Leave the receiver with L and load slot 2 again before a fresh attempt. Check that its count is zero. Inspect any already saved filename or occupied slot before sending again. Controller input is sent once, with no automatic replay after a timeout. Slower timing is available with `--prepare 0.20 --hold 0.40` at the end of the send command.
