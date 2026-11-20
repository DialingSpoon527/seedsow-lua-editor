# Install and open Artemis

Use these steps after manual entry, Pi entry, Pico entry, or [Plume USB entry](https://github.com/RealRobertBrownieJr/seedsow-artemis-plume-installer). Your configured uploader should already be saved and published in its own slot.

Keep your notes with the **uploader slot**, **Artemis slot**, **computer IP**, and **TCP port** beside you.

## 1. Start the sender on the computer

1. Connect the console and computer to the same reachable local network.
2. On the computer, open the **installer folder** containing `START_SENDER_WINDOWS.cmd`.
3. On Windows, double-click **START_SENDER_WINDOWS.cmd**. Alternatively, open a terminal there and run `py pc/send_alula.py`. On macOS/Linux, run `python3 pc/send_alula.py`.
4. Wait while it downloads and checks Alula’s pinned **v1** archive and prepares the files.
5. If the computer firewall asks, allow Python on your **private network**.
6. Look for an **Install run ID**, followed by **Listening at …**.
7. Keep this window open. Write down that run ID or leave it visible.

If you see an error instead of Listening, fix it before continuing. [Troubleshooting](05-troubleshooting.md) covers missing settings, download failures, and occupied ports.

### If the download fails

Download the original [v1 seedsow_save.zip](https://github.com/alula/switch-artemis-launcher/releases/download/v1/seedsow_save.zip) to your computer and leave it unchanged. Run the sender again with its actual path.

```powershell
py pc/send_alula.py --release "C:\Downloads\seedsow_save.zip"
```

On macOS/Linux, use `python3` and your own path. The sender checks this file against the same pinned checksum. Keep the computer and console connected to each other while using a local ZIP.

## 2. Run the uploader on the console

1. Leave any controller-transfer app idle after it has finished saving the file.
2. Open your ordinary Lua Editor, normally slot **1**.
3. Select **Choose slot** and enter your **uploader slot**.
4. Check that its source starts with the `PC_IP`, `TARGET_SLOT`, and `PC_PORT` settings you generated. `TARGET_SLOT` must be your separate **Artemis slot**.
5. Check again that the computer sender says **Listening**.
6. Select **RUN buffer** on the console once.
7. Watch the computer. It should report **Switch connected**, followed by the files being sent.
8. Let the transfer finish. The native uploader may not display progress on the console.

If it stays on Listening, the PC has accepted no connection. Recheck the address and port in the console copy, console network access, guest-network isolation, and firewall settings. The compact uploader has no connection/read timeout and may leave Seedsow frozen. Close the game with **HOME → X → Close** if it hangs, then inspect your settings before another attempt.

## 3. Check the installation result

1. After the PC reports transmission finished, fully close and reopen Seedsow.
2. Load your ordinary editor, normally **slot 1**. This also registers new published slots for the game’s load menu.
3. Select **File / new** and open `ax_install.log`.
4. View it in **TEXT** mode. Scroll to the end if needed.
5. Look for **ARTEMIS_INSTALL_COMPLETE SLOT=… RUN=…**.
6. Check that **SLOT** equals your Artemis slot and **RUN** matches the current sender window’s run ID.

A matching completion line confirms this installation attempt. If the line is missing, shows **FAILED**, or belongs to an older attempt, keep the log text and use [Troubleshooting](05-troubleshooting.md). A partial install can leave files occupying the destination. Check the error before trying another write.

## 4. Open Artemis

1. After confirming the completion log, return to the editor menu.
2. Select **Title screen**, then open the game’s **Load** menu.
3. Find your **Artemis slot**. Its title may look like **LUA … / ax_slot…lua**.
4. Load that slot.
5. Look for **switch-artemis-launcher by alula**.

Use your original editor slot whenever you want to return to the editor.

## 5. Start Artemis’s local server

1. On the Artemis screen, press **Y**.
2. Find the **console’s IP address** in the console’s Internet settings. This time, use the console address rather than the computer address you used earlier.
3. On the computer, open a browser.
4. Enter `http://YOUR_SWITCH_IP:8080/status`, replacing `YOUR_SWITCH_IP` with the console address.
5. Look for a response identifying the server and its endpoints.

For later sessions, load your Artemis slot and press Y again. Closing Seedsow stops the server. Keep the server on a trusted local network because its Lua execution endpoint accepts requests without authentication.

## Updates and recovery

This installation uses `ax_` filenames. Its update files are `ax_inject2.lua`, `ax_core2.lua`, and `ax_http2.lua`.

For this side-by-side installer, hold **Minus** while loading the Artemis slot to use its original launcher, core, and payload files. Check that the screen reports recovery mode. You can also select recovery on the launcher screen with Minus before starting HTTP. These options depend on the original installed files still being usable.

The [technical notes](06-technical-notes.md) explain the installed files and recovery behavior in more detail.
