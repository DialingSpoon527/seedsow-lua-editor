# Add the launcher to an existing Lua Editor save

This route keeps your Lua Editor and adds Alula's launcher to a free load-menu
slot. You run a small uploader once, then a computer sends the launcher over
the LAN. No new JKSV restore or console-to-console save transfer is involved.

If the editor is not already installed, use the
[first installation guide](01-first-install.md) instead.

## 1. Have these ready

- Your working Seedsow Lua Editor, with its ordinary program slots and templates.
- A Windows, Mac or Linux computer with Python **3.10 or newer**.
- A trusted LAN both the **console and computer** can reach. Avoid guest Wi-Fi
  that blocks communication between devices. Ethernet on the computer and Wi-Fi
  on the console are fine if they share the same LAN.
- Two different unused slots between **4 and 120**. Check the game's load menu
  and the editor's slot contents. Slots 4 and 5 may already contain examples.
- Your existing save backup, if available, and local copies of programs you care
  about. The installer adds files to the current save, but an interruption can
  leave a partial install. On Switch 1 you can make a full JKSV backup first.

The two slots have different purposes:

| Slot | What goes there | What happens later |
| --- | --- | --- |
| **Uploader slot** | Your generated small Lua program | You run it once to receive the install |
| **Launcher destination slot** | Alula's launcher, installed over TCP | You select it whenever you want to use Alula |

Keep slots **1–3** and any existing programs. The setup tool can check slot
numbers, but it cannot see which slots on your console are occupied.

The upstream launcher currently documents demo support, not full-game support.
An older report that the editor works in another edition is not a launcher
compatibility test. [Evidence and limits](06-technical-notes.md#hardware-evidence).

### Download and Python setup

1. Download this repository using **Code > Download ZIP**. Extract it into a
   new folder. Work in the extracted folder that contains this README and
   `SETUP_WINDOWS.cmd`; do not run the tools from inside the ZIP.
2. On **Windows**, install Python from [python.org](https://www.python.org/downloads/)
   if needed. In a terminal, `py --version` should show 3.10 or newer. If your
   installation only provides `python`, use that in place of `py` below.
3. On **Mac/Linux**, open Terminal and run `python3 --version`. Install or update
   Python if it is missing or older than 3.10.

The R14 tools need no `pip` packages or Tk. The optional older Pi companion uses
Tk; its separate setup is described in the [Pi guide](04-pi-upload.md).

To open a terminal in the extracted folder: on Windows, right-click its empty
background and choose **Open in Terminal**. On Mac/Linux, use `cd` followed by
the folder path; you can drag the folder into Terminal to insert its path.

### Find your computer's IPv4 address

Use the address of the **computer running the sender**, not the Switch or Pi.

- **Windows:** open Terminal, run `ipconfig`, and find **IPv4 Address** under your
  connected Wi-Fi or Ethernet adapter. Ignore disconnected adapters and VPNs.
- **Mac:** open **System Settings > Network**, select the connected interface,
  then **Details > TCP/IP** and note the IP address.
- **Linux:** check the connected interface in network settings, or use `ip -4 addr`.

Choose a private LAN address, usually starting with `192.168.`, `10.`, or
`172.16.` through `172.31.`. Leave the computer on this connection during the
install. If its address changes, generate and transfer the uploader again.

## 2. Generate your uploader

On Windows, double-click **SETUP_WINDOWS.cmd**. On Mac/Linux, run:

```sh
python3 tools/make_sheet.py
```

The setup asks for four values:

1. **Computer IPv4 address:** the address you just found.
2. **TCP port:** choose an unused port, preferably between **1024 and 65535**.
   Write it down. This is a temporary receiving port on the computer; it is
   separate from Alula's later HTTP port 8080 and the Pi bridge's port 39391.
3. **Free slot for Alula's launcher:** the unused destination slot you checked.
4. **Different free slot for the uploader:** the other unused slot.

The tool shows both slots and a character count, then creates:

| File in `build/` | Use |
| --- | --- |
| `VIEW_TYPING_SHEET.html` | Open in a browser for manual typing with checkboxes |
| `TYPE_IN_ORDER.txt` | Numbered text version of the same typing sheet |
| `ONE_ENTRY_PER_LINE.txt` | Exact keyboard chunks, without row numbers |
| `TYPE_THIS_EXACT.lua` | Complete configured uploader for Pi transfer |
| `config.json` | Settings the PC sender reads automatically |

Choose your entry method:

- [Manual entry with a controller or USB keyboard](03-manual-entry.md).
- [Send the Lua file with the Pi bridge](04-pi-upload.md).

After the uploader has been saved and published in its slot, return here.

## 3. Start the computer sender, then the uploader

1. Enable console Wi-Fi or Ethernet and connect it to the same reachable LAN as
   the computer. If you kept Wi-Fi disabled for Pi entry, enable it now.
2. On **Windows**, double-click **START_SENDER_WINDOWS.cmd**. On Mac/Linux:

   ```sh
   python3 pc/send_alula.py
   ```

3. The sender reads `build/config.json`, downloads and checks the pinned Alula
   **v1** save archive, then prepares the files. If Windows Firewall asks, allow
   Python on your **private network**. Other firewalls must allow incoming TCP
   to the port you chose. Router port forwarding is not needed.
4. Wait for **Listening at ...**. Note the **Install run ID** shown just above
   it. Keep this window open. If an error appears instead, fix it using
   [Troubleshooting](05-troubleshooting.md) before running the console uploader.
5. On the console, open your saved uploader program in the editor and choose
   **RUN buffer**. This is the small uploader slot, not the empty destination.
6. The computer should report **Switch connected**, then list transmitted
   files. The actual launcher transfer should be short once the connection is
   established; Pi entry is the slow part if you used it.

The compact native uploader has **no connection/read timeout**. A wrong IP,
closed sender or interrupted transfer can leave the game frozen. If it stalls,
close Seedsow with **HOME > X > Close**, check the settings and start the sender
again before trying a fresh run. Avoid repeatedly pressing Run.

### Alternative: use a ZIP you downloaded yourself

If automatic downloading fails, download the original
[Alula v1 seedsow_save.zip](https://github.com/alula/switch-artemis-launcher/releases/download/v1/seedsow_save.zip)
on the computer. Keep it unchanged, then run:

```powershell
py pc/send_alula.py --release "C:\path\to\seedsow_save.zip"
```

On Mac/Linux use `python3` and the actual file path. The sender still reads your
generated settings. It checks the same pinned ZIP hash for both methods; a
different release, Source code download or re-created ZIP will be rejected.
The computer can be disconnected from the internet for this method, while the
computer-to-console LAN connection remains available.

## 4. Finish the installation

**The computer's transmission message is not a console acknowledgement.** Check
the install result before launching the new slot.

1. Once transmission finishes, fully close and reopen Seedsow. Load your
   ordinary editor, normally **slot 1**. This lets the editor register the
   launcher's new slot in the game's load menu.
2. Use **File / new** to open `ax_install.log`. View it in **TEXT** mode. Look
   for `R14_COMPLETE SLOT=... RUN=...` at the end. The slot must be your launcher
   destination, and **RUN** must match the run ID from this sender attempt.
   Use the code window's scrolling controls if necessary. Leave the log as a
   log file; do not publish it as a program.
3. If the log says **R14_FAILED**, is missing, or has an older run ID, use
   [Troubleshooting](05-troubleshooting.md). Keep the full error text.
4. After a matching completion line, choose **Title screen** and open the game's
   **Load** menu. Find your destination slot. Its title may say
   **LUA ... / ax_slot...lua**; the number is the launcher slot you selected.
5. Load that destination slot. You should see **switch-artemis-launcher by alula**.

The editor launch in step 1 registers the slot added by this installer.

## 5. Use the launcher

1. On Alula's screen, press **Y** to start the HTTP server.
2. Find the **console's** IP address in its Internet settings. This time you
   need the Switch address, not the computer address used for the uploader.
3. On the computer, open `http://YOUR_SWITCH_IP:8080/status` in a browser.
   Replace `YOUR_SWITCH_IP` with that address. The response should identify the
   Seedsow/Nora HTTP server and list its endpoints.

If you downloaded this repository, you can send its small `examples/hello.lua`
test from the project folder. Replace `YOUR_SWITCH_IP` with the console address.
On Windows PowerShell:

```powershell
curl.exe -X POST "http://YOUR_SWITCH_IP:8080/eval" --data-binary "@examples/hello.lua"
```

On Mac/Linux:

```sh
curl -X POST "http://YOUR_SWITCH_IP:8080/eval" --data-binary "@examples/hello.lua"
```

The response should show `status: ok` and `hello world`. See
[Alula's HTTP examples](https://github.com/alula/switch-artemis-launcher#interacting-with-http-server)
for file upload and Lua execution.

Use only trusted scripts and keep port **8080** on a trusted LAN: `/eval` runs
incoming Lua without authentication. Closing Seedsow stops the server. Later,
select the launcher slot again and press Y; the one-time uploader is no longer
needed for ordinary launches.

## Updates and recovery

This side-by-side install uses `ax_` filenames. Its update files are
`ax_core2.lua`, `ax_http2.lua` and `ax_inject2.lua`, rather than the unprefixed
names in Alula's replacement-save instructions.

Hold **Minus** while loading the launcher slot to ignore `ax_inject2.lua` and
use the original core/payload files as well. The screen reports recovery mode;
press Y to start HTTP using those original files. You can also press Minus on
the launcher screen before Y to ignore core/payload updates for that launch.
Your original Lua Editor remains available through its own slots.

For advanced command options and the files installed, see
[technical notes](06-technical-notes.md).
