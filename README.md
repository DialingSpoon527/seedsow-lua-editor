# Add Alula’s Artemis launcher to your Lua Editor

> **This project is practically all AI-written.** I give Codex the direction and test what I can; almost all of the code, tools, and instructions here were written by AI. I cannot guarantee that it works or is safe on your setup, but the base principles are sound. Other people’s upstream work is credited separately.

This guide starts with the **Seedsow Lua Editor already working on your console**. It adds Alula’s launcher to a free slot in that save.

**The rewritten instructions, updated Pi service, and new Pico sender still need a complete hardware walkthrough.** The compact uploader has previous hardware reports. Offline tests cover the controller transports and installation logic; those checks do not establish hardware compatibility.

## Start here

1. Follow **[Prepare your computer and editor](docs/02-existing-editor.md)**. It explains the downloads, Python, finding your computer’s address, and choosing two free slots.
2. Choose **one** way to put the small uploader into the editor.

| Method | What you use | Instructions |
| --- | --- | --- |
| Manual entry | An ordinary controller or a USB keyboard | [Type the uploader](docs/03-manual-entry.md) |
| Raspberry Pi | A full Raspberry Pi running Linux and acting as a Bluetooth controller | [Send with a Pi](docs/04-pi-upload.md) |
| Pico 2 W, standalone | Pico 2 W plus USB data cable; no UART adapter or jumper wires | [Configure, flash and send](docs/09-pico2w-standalone.md) |
| Pico, externally controlled | An RP2040 Pico or RP2350 Pico 2 W with a USB-to-UART adapter, or an existing compatible wireless HTTP bridge | [Set up and send with a Pico](docs/07-pico-upload.md) |
| Plume USB | A modded Switch 1 running Plume USB, connected to the target console as a USB keyboard | [RealRobertBrownieJr’s Plume walkthrough](https://github.com/RealRobertBrownieJr/seedsow-artemis-plume-installer) |

3. Follow **[Install and open Artemis](docs/08-finish-installation.md)**. All methods finish with these steps; the standalone guide explains which PC sender to start before returning to them.

The Plume walkthrough supplies numbered text chunks for the uploader. Follow its setup instructions and check that the chunks use your computer’s IP, the same TCP port as your sender, and your chosen Artemis destination slot. Its example uses uploader slot **21**, Artemis slot **20**, and port **39000**. Keep those settings consistent with your local setup before sending anything.

The small uploader contains your computer’s address and the slot for Artemis. Once it is saved, your computer sends the launcher files over your local network. Allow plenty of time for typing or controller transfer. The network transfer afterward is much shorter.

A full Raspberry Pi and a Pico are different devices. Choose the Pi guide if your board runs Raspberry Pi OS. Choose the Pico guide if you have a small microcontroller with a BOOTSEL button.

For **Pico 2 W without an adapter**, use the standalone guide and run `SETUP_PICO2W_STANDALONE.cmd` to create your configured UF2. It stores the uploader on the board and uses BOOTSEL for a button test, calibration and deliberate transfer start. The separate UART option still uses a 3.3 V USB-to-UART adapter and the PC sender commands. Both Pico 2 W builds pass compilation and offline checks; physical input and a complete transfer still need hardware testing. Their Wi-Fi and Bluetooth are unused.

## Before you change anything

Keep slots **1–3** and any programs you want. Check that both new slots and your uploader filename are unused. Back up your save if you already have a working way to do that. Keep copies of important Lua programs separately. An interrupted install can leave files behind in the save.

The upstream project lists **Seedsow Lullaby Demo**, title ID `010042D022AEA000`. Check your game against that supported title. Existing Lua Editor operation alone does not establish Artemis compatibility with another game edition. [Alula’s supported games](https://github.com/alula/switch-artemis-launcher#supported-games)

This workflow uses your installed editor and local network throughout. Keep the computer, console, and any wireless bridge on a trusted network. Alula’s HTTP server accepts Lua execution requests from machines that can reach it.

## If you get stuck

Use the exact screen text or the last line in the PC window to find the matching entry in **[Troubleshooting](docs/05-troubleshooting.md)**.

[Technical notes](docs/06-technical-notes.md) describe the files and test evidence. [Third-party notices](THIRD_PARTY_NOTICES.md) cover the external projects used here.
