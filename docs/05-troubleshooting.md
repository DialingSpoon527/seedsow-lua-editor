# Troubleshooting

## Windows closes the setup window or cannot find Python

Open Terminal in the extracted installer folder and run `py --version`, then
`py tools/make_sheet.py`. You need Python 3.10+. If your installation provides
`python` instead of `py`, use `python tools/make_sheet.py` and
`python pc/send_alula.py`. The `.cmd` shortcuts use `py`.

On Mac/Linux, use `python3`. Neither installer tool needs Tk or pip packages.

## “Run tools/make_sheet.py first”

Generate your settings before starting the sender. The default settings file
is **build/config.json** in this installer folder. If you used another output folder,
pass its config explicitly, for example:

```sh
python3 pc/send_alula.py --config "/path/to/your/config.json"
```

The settings determine the Lua source. If you change the computer IP, port or
launcher destination, generate the uploader again and update the console copy
as well. For manual entry, its first three settings entries can be replaced
carefully; compare with the regenerated sheet and final byte count.

## Download or checksum error

The sender requires the original **v1 seedsow_save.zip**. Use the
[local ZIP option](02-existing-editor.md#alternative-use-a-zip-you-downloaded-yourself)
if the automatic download is blocked. A Source code ZIP, Nora save, newer version
or re-compressed ZIP is not the pinned file. Do not bypass the checksum to make
an unexpected download pass.

## “Address already in use” or a bind error

Close an older copy of the sender or the other program using your chosen port.
If the computer no longer owns the IP you generated, reconnect it to the expected
network or generate new settings. A new TCP port also needs an updated console
uploader. Ports below 1024 can require extra privileges on Linux/Mac; choosing
another unused port above 1023 is simpler.

## Sender says Listening, but the console never connects

Check these before a fresh attempt:

1. The console uploader's **PC_IP** is the **computer's** active LAN IPv4 address.
2. **PC_PORT** matches the sender's listening port.
3. The console has an active Wi-Fi/Ethernet connection, even if you used Bluetooth
   alone to enter the uploader.
4. Both devices are on a LAN that permits device-to-device connections. Guest
   Wi-Fi, client isolation and VPN routing can prevent this.
5. The computer firewall permits Python/incoming TCP on that port on the private
   network. Leave router port forwarding off.

The compact uploader has no timeout and does not reliably report connection
errors. Close Seedsow with **HOME > X > Close** if it hangs. Restart the sender
first, wait for Listening and then run a fresh console attempt.

## Transmission ends but there is no matching completion log

Open **ax_install.log** in the ordinary editor through **File / new**. Its
`ARTEMIS_INSTALL_COMPLETE SLOT=... RUN=...` line must match this sender attempt's run ID and
your chosen destination. An older successful log is not a result for a new attempt.

If the file is missing, the receiver may not have reached the installer or the
game may have crashed. Recheck hand-typed text against the sheet, including its
byte count. Preserve an available error log before changing files.

## `SLOT_IN_USE` or `SOURCE_IN_USE`

The destination contains save files or a sidecar source already. Choose a
different unused destination slot, regenerate the uploader and transfer or edit
that source before trying again. A slot can contain files even when its menu
entry is missing. Keep the uploader and launcher slots different.

The installer refuses an occupied destination rather than replacing it.

## `COLLISION ax_...`

An existing launcher file has different contents. This can be an earlier install
or a different version; a different destination slot alone will not resolve a
shared `ax_` file conflict. Keep the log and back up the existing files before
deciding what to replace. Do not delete recovery/editor files to work around it.

## Missing bootstrap, slot template or thumbnail

The installer expects the original editor's `ssNNN.asb`, `ssseedNNN.bin` and `ssethumb.png`
files. Changing only the visible slot number cannot create missing templates.
Keep your working save and check the
[original editor's recovery instructions](https://github.com/DialingSpoon527/seedsow-lua-editor/blob/88f443f8666bf02ebc9cb1887a470958739a0121/docs/04-updates-recovery.md)
or report the exact error and editor version. Another editor layout may need
adaptation; do not restore a starter save over programs you want to retain.

## Completion log matches, but no launcher slot appears

Fully close and restart Seedsow, load the ordinary editor in slot 1, then use
**Title screen** and open the game's **Load** menu. Loading the editor registers
the new `.ref` file in the menu. Find the destination number you selected; the
title can contain `ax_slot...lua` rather than “Artemis”.

## Launcher opens but `/status` does not respond

Press **Y** on the launcher screen and read any error shown. Use the **Switch's**
current IP in `http://YOUR_SWITCH_IP:8080/status`; this is different from the
computer IP used for the installer. Keep both on the same reachable LAN. If the server
reports a native error, retain that message and your game/firmware details.

The installer port and Pi port 39391 are not the HTTP server port. Closing the
game stops the server.

## Pi upload errors

Use the companion from its **separate editor folder**. Import the correct
connection JSON, make the Pi Player 1, and load slot 2 until it shows
**PC INPUT: 0 / ? bytes**. Confirm success on the console, not only in the app.
After an interrupted controller upload, leave with L and reload slot 2 before
trying Slow speed. See the [Pi walkthrough](04-pi-upload.md).

## Returning to your editor

Close Seedsow and load the editor's original slot 1 or backup slot 3. The sidecar
does not change game startup. For launcher update recovery, use the
[Minus-button steps](02-existing-editor.md#updates-and-recovery).
