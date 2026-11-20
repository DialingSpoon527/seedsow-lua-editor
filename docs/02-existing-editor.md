# Prepare your computer and editor

Do this once, whichever entry method you choose. By the end, your computer will have created a small Lua uploader with the right settings for you.

## 1. Check your starting point

1. Open Seedsow under the profile containing your Lua Editor.
2. Load your ordinary editor, normally slot **1**.
3. Check that you can see its menu and your saved programs.
4. Keep this profile selected for the entire installation. Saves belonging to different profiles are separate.
5. If you already have a working save backup tool, make a backup. Save important programs separately too. Adding files to the save can leave a partial installation if interrupted.

## 2. Download and extract the installer

1. On your computer, download [the installer ZIP](https://github.com/DialingSpoon527/seedsow-lua-editor/archive/refs/heads/artemis-installer.zip).
2. Find the downloaded ZIP in Downloads.
3. On Windows, right-click it and choose **Extract All**, then **Extract**. On macOS, double-click it. On Linux, use your archive manager’s **Extract** command.
4. Open the extracted folder. If it contains one more folder, open that too.
5. Stop when you can see **README.md**, **SETUP_WINDOWS.cmd**, **pc**, **tools**, and **docs** together. This is the **installer folder** mentioned below.

Work with the extracted files. Keep this folder available until installation finishes.

## 3. Check Python

You need Python **3.10 or newer** on the computer.

### Windows

1. In the installer folder, click File Explorer’s address bar.
2. Type `powershell` and press Enter. A terminal opens in that folder.
3. Type this and press Enter.

   ```powershell
   py --version
   ```

4. Look for a Python version of 3.10 or newer. If Windows cannot find Python, install it from [python.org](https://www.python.org/downloads/windows/), then close and reopen the terminal.
5. If `python --version` works but `py --version` does not, use `python` wherever these guides show `py`. Run the Python commands directly instead of the `.cmd` shortcuts.

### macOS or Linux

1. Open Terminal.
2. Type `cd `, including the space, then drag the installer folder into the terminal. Press Enter.
3. Run `python3 --version`.
4. If Python is missing or older than 3.10, install a current Python 3 for your operating system before continuing.

Keep this terminal open. All commands below run from the installer folder. The setup and final network sender use Python’s standard library. The wired Pico path adds one serial package, and the Pi companion uses Tk for its window.

## 4. Write down your computer’s address

The console must connect to the **computer running the network sender**.

| Computer | How to find its IPv4 address |
| --- | --- |
| Windows | Run `ipconfig`. Find **IPv4 Address** under the connected Wi-Fi or Ethernet adapter. |
| macOS | Open **System Settings → Network**, select the connected Wi-Fi or Ethernet connection, then **Details → TCP/IP**. |
| Linux | Open network settings, select the connected network, and look for IPv4 details. |

Use your active home-network address, usually starting with `192.168.`, `10.`, or `172.16.` through `172.31.`. Ignore VPN and disconnected adapters. Keep the computer on this connection until you finish.

Also connect the console to the same reachable local network. A wired computer and a wireless console can work together. Guest Wi-Fi may prevent devices from contacting one another.

## 5. Choose two empty slots

1. Look through your editor and the game’s load menu.
2. Choose two **different unused slots from 4 through 120**. Existing example programs count as occupied.
3. Write the numbers down with these names.

| Name | What you will put there |
| --- | --- |
| **Uploader slot** | The small Lua file you type or send with a controller |
| **Artemis slot** | The launcher installed by the network transfer |

For example, you could use uploader slot **20** and Artemis slot **21**, **if both are empty on your console**. Substitute your own numbers whenever a later example uses 20 or 21. Keep slots 1–3 for the editor and recovery programs.

## 6. Generate the uploader

If you plan to use the external Plume guide’s numbered files, check [its configuration](https://github.com/RealRobertBrownieJr/seedsow-artemis-plume-installer) first. Its example uses TCP port **39000**, Artemis slot **20**, and uploader slot **21**. Choose empty slots on your console and make the Plume text and the settings below agree, including your computer’s current IP.

1. On Windows, double-click **SETUP_WINDOWS.cmd** in the installer folder. If you use the terminal instead, run `py tools/make_sheet.py`. On macOS/Linux, run `python3 tools/make_sheet.py`.
2. Enter the **computer’s IPv4 address** from step 4.
3. Enter a TCP port. **40000** is an example you can use if it is free. Keep a note of your choice.
4. Enter the **Artemis slot**, meaning the final launcher destination.
5. Enter the **different uploader slot**.
6. Check the displayed summary against your notes.
7. Open the new **build** folder inside the installer folder.

You should find these files.

| File | What you use it for |
| --- | --- |
| **VIEW_TYPING_SHEET.html** | Open this in a browser for manual entry |
| **TYPE_IN_ORDER.txt** | A plain-text copy of the numbered typing sheet |
| **TYPE_THIS_EXACT.lua** | The complete file for Pi or Pico transfer |
| **config.json** | Settings used by the final network sender |

The script prints a final character count. Keep it available for checking your console copy. If your computer address, chosen port, or Artemis slot changes later, regenerate the uploader and update the console copy before running it.

## 7. Choose one entry method

- [Manual entry](03-manual-entry.md) using your controller or USB keyboard.
- [Pi Bluetooth entry](04-pi-upload.md) using a full Raspberry Pi.
- [Pico entry](07-pico-upload.md) using a wired microcontroller or compatible HTTP bridge.
- [Plume USB entry](https://github.com/RealRobertBrownieJr/seedsow-artemis-plume-installer) using a modded Switch 1 as a USB keyboard. Follow that community guide to transfer its numbered text chunks, checking its IP, port, and destination settings against your setup.

Each method ends with the uploader saved in your chosen slot. Then follow [Install and open Artemis](08-finish-installation.md).
