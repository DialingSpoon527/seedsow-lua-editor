# Later updates and recovery

**First time here?** Follow [beginner installation](01-console-install.md) with
**Seedsow-Lua-Editor-Save.zip**. You can leave this page until the editor works
on your console. The PC companion is optional.

If the editor is already installed, keep your save and programs. An editor
update is an ordinary `.lua` program saved into a **fresh user slot**, such as
30. Slots 1-3 and your last working editor stay available for recovery.

## Updating ordinary programs

Open the source in the console editor, change it, and choose **Save + publish**.
With optional Pi uploads, send the new source to the intended filename and user
slot instead. In both cases, restart the game and reload that slot when you
want to verify it was kept.

## Choose an editor update method

| Method | What you need | What happens to your console save |
| --- | --- | --- |
| Wired USB keyboard | Update Lua source to read and type | Enter and publish the update on the console; existing programs stay. |
| Controller character grid | Update Lua source to read | Enter the same source with the grid; existing programs stay. Slowest method. |
| Optional PC/Pi upload | Windows companion and configured Pi | Send the Lua into a fresh slot; existing programs stay. |
| Restore an updated save ZIP | Hacked Switch 1 and JKSV; transfer again if using Switch 2 | Replaces the console save with that ZIP's contents. Back up first. |

The first three methods work through an installed editor on Switch 2 without
bringing back the original Switch 1. The update must match your retained editor
base and the slot it was built for. A slot-30 update must be published to slot 30.

## Get the update Lua

If your download includes **Editor-Update-slot-30.lua**, follow its accompanying
README and use slot 30. This file runs inside Seedsow; it is not a Windows app.

Otherwise, extract **Seedsow-PC-Companion-and-Source-VERSION.zip** on your
computer and open **START WINDOWS.cmd**. Older releases call this PC bundle
`seedsow-lua-editor-VERSION.zip`.

1. In **Install save & updates**, select the starter ZIP you originally installed
   or a backup matching its base. You do not need a new Switch 2 export merely
   to target the retained base.
2. Choose an unused **New editor slot**, then **Build update & open for sending**.
3. The app displays the generated `.lua` path. Use that file with any entry
   method below. Building it requires no Pi connection.

Developers can also [build from the command line](06-development.md#build-an-alongside-editor-update).

## Enter the update on the console with a USB keyboard

1. Load your working editor. Choose the unused slot specified by the update.
2. Use **File / new** to open a new plain filename, such as `update30.lua`.
   Start with an empty buffer. If prompted about unsaved sample text, repeat
   the action after releasing the button to discard that sample.
3. Choose **Keyboard +** and type the update's source exactly, including
   punctuation and line breaks. For a long file, enter it in consecutive chunks
   of at most **32 characters**, finishing each dialog before starting the next.
   The cursor moves to the end of each insertion. Do not include Markdown fences.
4. Use **Save file** to keep progress. When the complete file is entered, choose
   **Save + publish**, then load that numbered slot from the game's load menu.
5. Check the update header, publish a tiny program into another unused slot,
   then fully restart Seedsow and reload both the update and that program.

A Windows clipboard does not paste directly into the console's text dialog.
This game's Switch keyboard is capped at **32 characters per dialog**. The
editor's `textfieldsize` value does not enlarge that native keyboard. Entering
an update this way takes many separate insertions; the Pi uploader handles
larger files without using the system keyboard.

## Enter the update with the controller grid

Use the same empty-file, save and publish steps above. Enter the complete source
with the on-screen character grid instead of **Keyboard +**. **ENTER** inserts
a newline, **TAB** inserts a tab, and **BKSP** corrects mistakes. Save progress
often. This needs no keyboard, computer connection or Pi, but a multi-kilobyte
editor update takes substantial manual entry.

## Upload with the optional PC/Pi companion

Follow [send a file](03-send-files.md), selecting the generated update Lua and
its matching fresh slot. Arm receiver slot 2, send, and wait for **PC FILE SAVED**
on the console. Hold L to leave the receiver, then load the destination slot.
Transfers are slow and depend on file size; use the companion's time estimate.
Check saving and restart as described above.

## Restore a save ZIP containing the update

Use this route when you can restore with JKSV and accept replacing the whole
console save. Follow the backup/restore steps in the [installation guide](01-console-install.md).
For **Seedsow-Lua-Editor-Update-Save.zip**, load slot 1 once to register entries,
choose **Title screen**, then load the update slot named in its README.

The ZIP only contains programs present in the backup used to build it. Restoring
a starter-based ZIP over your current save does not preserve newer console
programs. Use one of the Lua entry/upload methods to keep those programs.

Fresh saves already include the current editor in slot 1. Existing installations
can add it using one of the methods above. See [line movement and code scrolling](07-console-editor.md#scrolling-and-moving-between-lines).
It has passed automated checks; its console trial is pending. It reconstructs
and checks its source before starting, keeps separate settings/reports, and
attempts to restore the prior editor if startup fails. It does not fetch updates.

## Keep the recovery base

The updated editor still boots through the retained base loader. Its normal
storage operations avoid overwriting base recovery files, and it blocks
publishing over its own active slot. Use another slot for the next version.
Compatible updates can be installed later this way, but arbitrary future game
or editor changes are not guaranteed to fit the same loader.

| If this happens... | Try this |
| --- | --- |
| A program reports an error | Press B or reload editor slot 1 or 3. |
| An upload fails | Stop sending, hold L, reload receiver slot 2 at zero, then resend. |
| An editor update fails to reconstruct or start | Reload the working editor in slot 1 or 3. |
| One or two base core copies are damaged | A valid remaining copy can start and repair the others. |
| All working launchers/core copies are lost | Restore your external backup using your available save-restoration route. |

This is a way to keep extending an installed editor, not a promise that save
data cannot be deleted or corrupted. Unrestricted Lua can bypass ordinary file
protections. Retain slots 1-3, a working update slot, and your backup.
