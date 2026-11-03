# Send the small uploader with the Pi bridge

The Pi sends controller inputs to the editor's existing receiver. It transfers
the roughly 3,700-character uploader, then the **computer sends the larger
launcher files directly over the LAN**. You do not need to send the complete
launcher through Bluetooth controller inputs.

First complete [existing-editor setup](02-existing-editor.md#2-generate-your-uploader)
to create **build/TYPE_THIS_EXACT.lua**. Keep a note of your two chosen slots.

## 1. Open the existing Pi companion

If your Pi bridge is already working, use your existing companion folder and
connection settings. Leave this R14 folder separate: its `pc/` directory contains
the new network sender, while the older companion has its own `pc/app.py`.

If you need the companion files, download
[Seedsow-PC-Companion-and-Source-0.1.3.zip](https://github.com/DialingSpoon527/seedsow-lua-editor/releases/download/v0.1.3/Seedsow-PC-Companion-and-Source-0.1.3.zip)
and extract it into a **separate folder**. The companion's connection and sending
tabs are the parts used here.

- **Windows:** open **START WINDOWS.cmd** in that companion folder.
- **Mac:** in that companion folder, run `python3 pc/app.py`. The reported Mac
  setup used `brew install python-tk` to add Tk to its Python installation.
  Use a Python 3.10+ interpreter with working Tk.
- **Linux with a desktop:** use Python 3.10+ with Tk, then run
  `python3 pc/app.py` in the companion folder. On Debian-based systems, Tk is
  commonly installed with `sudo apt install python3-tk`.

If you have a private connection JSON from your existing Pi, select **Import
connection file…**, then **Save & test connection**. Keep this file private.

### Setting up a Pi for the first time

Manual typing is available if you do not want to set up a Pi just for this step.
For a new Pi setup, use the companion's included `docs/02-pi-setup.md` or the
[original editor's Pi guide](https://github.com/DialingSpoon527/seedsow-lua-editor/blob/88f443f8666bf02ebc9cb1887a470958739a0121/docs/02-pi-setup.md).
The working reference used a Pi 3B's built-in Bluetooth and Raspberry Pi OS.
Not every Bluetooth adapter works with controller emulation.

The process is:

1. Connect the Pi to your LAN and enable SSH.
2. Copy the extracted **companion source folder** to the Pi, then SSH to it.
3. In that folder on the Pi, run `sudo sh pi/install.sh`. It installs the bridge
   service and required packages. Bluetooth may restart during installation.
4. Export its connection file with
   `python3 pi/export_connection.py --output ~/seedsow-connection.json`.
5. Copy the JSON back to your computer, import it into the companion and test
   the connection. The linked guide gives the exact copy and SSH commands.

The bridge uses authenticated HTTP on Pi port **39391** on your trusted LAN.
This is separate from the TCP port chosen for R14 and Alula's HTTP port 8080.

## 2. Pair and calibrate

1. Open **Controllers > Change Grip/Order** on the console.
2. In the companion's **Optional: connect Pi** tab, click **Pair controller**.
   Put other nearby paired consoles to sleep if the Pi connects to the wrong one.
3. Make the Pi **Player 1**, then return to Seedsow. If you use airplane mode
   for controller entry, enable its Bluetooth/controller exception.
4. Load **slot 2: PC INPUT / CALIBRATE**.
5. If the screen says **INPUT CALIBRATION**, waiting for physical A, tick the
   companion's matching confirmation box and click **Calibrate controller**.
   Release all other controls and wait roughly 18 seconds.
6. Continue when the console says **PC INPUT: 0 / ? bytes**. If it already said
   that before calibration, it had a saved mapping and was ready. A stale
   “hold R” heading can remain above the ready line.

Your computer and Pi need their LAN connection during this step. The console
only needs Bluetooth for the controller upload; it needs its LAN connection
when you run the R14 uploader afterward.

## 3. Send your generated Lua file

1. In the companion, open **Optional: send files**, then **Open file…**.
2. Select **TYPE_THIS_EXACT.lua** from the **new R14 folder's build directory**.
   The file starts with your generated `PC_IP`, `TARGET_SLOT` and `PC_PORT`.
3. Select **Lua launch slot**. Set **Slot** to the free **uploader slot** you
   chose during R14 setup. The app's default slot may be different; change it.
4. Use a new filename such as **artemis-uploader.lua**. Confirm both that name
   and the uploader slot are free; sending publishes to the selected slot.
5. Start with **Normal** speed. Confirm the console receiver still shows
   **PC INPUT: 0 / ? bytes**, then tick the ready box.
6. Click **Send & save**. Release console controls and keep both devices awake.
   Controller entry can take many minutes; let the companion finish.
7. Confirm **PC FILE SAVED** on the **console**, including the expected byte
   count, filename and uploader slot. The companion's progress only describes
   what the Pi sent.
8. Hold **L** to leave the receiver. The companion's **Controller** tab has
   **Hold L / leave receiver** if needed.

If it fails partway through, stop sending, hold L to exit, then load slot 2 again
to get a new zero-count receiver before retrying. **Slow** gives more timing margin.

## 4. Run the network installation

1. Enable console Wi-Fi or Ethernet and connect it to the computer's LAN. If
   airplane mode left Wi-Fi disabled, enable the required network connection now.
2. Return to your **R14 folder** on the computer. Start
   **START_SENDER_WINDOWS.cmd**, or `python3 pc/send_alula.py` on Mac/Linux.
3. Wait for **Listening** before running anything on the console.
4. Load your ordinary editor, select **Choose slot** and open the **uploader
   slot** you just sent. Check it contains your generated source, then choose
   **RUN buffer**.

Continue with [the installation log and launcher steps](02-existing-editor.md#4-finish-the-installation).

Once installed, ordinary launcher use goes through its destination slot and
HTTP server; you can leave the Pi bridge off when you are not using it.
