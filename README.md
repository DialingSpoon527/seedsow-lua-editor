# ⚠️ AI-generated instructions — not yet human-reviewed

> **The proven single-line R14 script is confirmed working on hardware.**
> The instructions and Pi setup material are currently AI-generated and have
> **not yet been human-reviewed**. You're welcome to try them.

# Seedsow Artemis Installer

**First time here? Start with [Alula's switch-artemis-launcher](https://github.com/alula/switch-artemis-launcher/) and download its `seedsow_save.zip`.**

Our [step-by-step first installation guide](docs/01-first-install.md) explains
how to restore that download with JKSV on Switch 1 and transfer it to Switch 2.
Use Alula's save for a new installation; the tools here are for people who
already have the Seedsow Lua Editor.

## Already have the Lua Editor?

This installer adds Alula's launcher to a **free program slot in your existing
save**. You keep the editor, its recovery slots and your programs. The launcher
runs when you select its slot; game startup stays as it is.

You enter a small R14 uploader once, then your computer sends the launcher over
your local network. Choose either way of getting that uploader onto the console:

| Method | What you need | Start here |
| --- | --- | --- |
| **Manual entry** | Computer, console editor, controller or USB keyboard; roughly 3,700 characters in entries of up to 32 | [Existing-editor setup](docs/02-existing-editor.md), then [typing guide](docs/03-manual-entry.md) |
| **Pi bridge** | Existing editor plus the Bluetooth Pi upload setup | [Existing-editor setup](docs/02-existing-editor.md), then [Pi guide](docs/04-pi-upload.md) |
| **Replace the save** | Modded Switch 1 and willingness to replace the current game save | [First installation guide](docs/01-first-install.md) using Alula's download |

Both uploader methods need the **console and sending computer on the same
reachable LAN**. The Pi only enters the small uploader; the launcher files travel
directly from the computer to the console over TCP.

You can keep using your current editor until you want to install the launcher.
The editor's source and original guides remain on
[`main`](https://github.com/DialingSpoon527/seedsow-lua-editor/tree/main).
The [v0.1.3 release](https://github.com/DialingSpoon527/seedsow-lua-editor/releases/tag/v0.1.3)
still contains the editor save and Pi companion.

## Quick start for an existing editor

1. Download this repository with **Code > Download ZIP**, then extract it on
   your computer. Open the extracted folder containing this README.
2. Check **two different unused slots**, both between 4 and 120: one for the
   small uploader and one for Alula's launcher. Keep slots 1–3 for recovery.
3. Run **SETUP_WINDOWS.cmd**, or run `python3 tools/make_sheet.py` in a terminal
   on Mac/Linux. Enter your computer's LAN IPv4 address, a TCP port and the two
   slots. [Detailed setup](docs/02-existing-editor.md#2-generate-your-uploader).
4. [Type the generated sheet](docs/03-manual-entry.md) or
   [send the generated Lua file with the Pi](docs/04-pi-upload.md).
5. Start **START_SENDER_WINDOWS.cmd**, or `python3 pc/send_alula.py` on Mac/Linux.
   Wait for **Listening**, then run your uploader on the console.
6. Check the install log, register the new slot and start the launcher using
   [the finishing steps](docs/02-existing-editor.md#4-finish-the-installation).

The [full walkthrough](docs/02-existing-editor.md) includes Python setup, finding
your IP address, firewall settings, a local-download option and expected screens.
If something stalls, use [Troubleshooting](docs/05-troubleshooting.md).

## What is supported?

The new-install route follows Alula's **Seedsow Lullaby demo** support. Its
[README](https://github.com/alula/switch-artemis-launcher#supported-games) lists
demo title ID `010042D022AEA000`; it currently says the full game is unsupported.
The old Lua Editor's compatibility reports do not establish launcher support.

R14's supplied test report records a working Switch 1 install and HTTP `/status`
response, plus a successful manually typed install on an unmodified Switch 2.
Exact editor, game-region and firmware coverage was not supplied. The desktop
cleanup in this repository still needs a new end-to-end console trial; see
[technical notes](docs/06-technical-notes.md).

This installer downloads and checks the original **Alula v1** Seedsow archive.
It does not silently switch to a newer release. Generated source, typing sheets
and settings stay in the ignored `build/` folder.

## Network use

Use a trusted LAN. Alula's HTTP server on port **8080** can execute Lua sent to
`/eval` without authentication. Keep it and the temporary uploader port off the
public internet. The compact uploader has no connection timeout: start the PC
sender first, and close Seedsow if an upload hangs.

For credits, third-party material and licensing, see
[Third-party notices](THIRD_PARTY_NOTICES.md).
