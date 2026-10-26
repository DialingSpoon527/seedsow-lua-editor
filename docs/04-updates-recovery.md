# Later updates and recovery

You can leave updates until after the editor is installed. Ordinary Lua
programs, files and compatible editor updates can be saved through the editor
itself, without restoring another whole save or bringing back the original
Switch. Keep a working editor available while trying a new one.

## Updating ordinary programs

Open the source in the console editor, change it, and choose **Save + publish**.
With optional Pi uploads, send the new source to the intended filename and user
slot instead. In both cases, restart the game and reload that slot when you
want to verify it was kept.

## Installing an updated editor alongside the working one

An editor update is itself a Lua program. Put it in a **fresh user slot**, such
as 30, keeping recovery slots 1-3 and your last working editor intact.

1. Extract the new release on your PC and open **START WINDOWS.cmd**.
2. In **Install save & updates**, choose a backup matching the editor base
   installed on your console.
3. Choose a fresh **New editor slot** and click **Build update & open for sending**.
4. If you use a Pi, follow the [file-upload guide](03-send-files.md) to send the
   update to that slot. Expect roughly 25-36 minutes for a 5.6 KB file.
5. Without a Pi, the generated Lua is still an ordinary source file: open a new
   file in the console editor and enter the complete source with **Keyboard +**
   in multiple insertions, or the character grid. Keep each keyboard entry
   below the dialog's 2,048-character limit. This is slow, but uses the installed
   editor alone. A Windows clipboard does not paste directly into the console.
6. Choose **Save + publish** for the new slot, then load it.
7. Check the updated editor, publish a tiny program in another free slot, and
   verify that both reload after restarting the game.

The current update builder has passed local checks; this alongside-editor
workflow still needs its console trial. It reconstructs and checks the source
before starting it, uses separate settings/reports, and attempts to return to
the prior editor if startup raises an error. It does not fetch updates for you.

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
