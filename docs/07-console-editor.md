# Use the console editor

Manual editing needs no network or Pi. Load slot **1** or **3** for the ordinary
editor. Slots 1–3 are reserved for editor recovery; use **4–120** for programs.

## Write and keep a program

1. Choose a free user slot.
2. Select **Keyboard +** to insert text at the byte cursor. A wired USB keyboard
   can type into the console's text-entry dialog. **Edit line** changes the
   current line, up to 512 bytes, while keeping the rest of the file.
3. The on-screen character grid is available for printable ASCII, newline,
   tab and backspace.
4. Choose **RUN buffer** to run the current contents, including unsaved edits.
5. Choose **Save + publish** to save the source and create a normal load-menu
   entry for your selected slot. **Save file** writes the file without publishing.
6. Restart Seedsow and load your numbered slot to run the saved program.

User source filenames default to `sscode004.lua` and similar names. A
`ssslot004.ref` file records the source filename for that slot. **File / new**
can open another plain filename; a missing file starts a new buffer.

## Controls

| Input | Action |
| --- | --- |
| Touch, or D-pad then A | Select and activate a button |
| B | Backspace while editing; return from a normally running program |
| L / R | Move the byte cursor |
| X | Open console text entry |
| Y | Run the buffer |
| Byte offset | Move to a zero-based byte position |
| Undo | Restore one of the last 12 in-memory edits |

Unsaved changes require a repeated open/navigation action before discarding.
**Restore .bak** loads the previous file version into the buffer for inspection.

## Raw hex editing

**TEXT / HEX** changes how bytes are displayed and entered. In HEX mode, enter
two hex digits per byte; `00` is supported. **Keyboard +** accepts pairs of hex
digits separated by whitespace. **INSERT / PATCH** selects insertion or
overwrite. Patching past EOF extends the file.

Files are bounded at **1 MiB**; writable plain filenames at **72 characters**
inside the console editor. The PC uploader uses a stricter 64-character limit
to leave space for transfer metadata. Raw writes store literal bytes and do not
repair file formats. Use **Save file** for raw native-save bytes; publishing
requires a separate Lua source filename.

## Lua program interface

```lua
print("Hello")
local data = editor.read("notes.txt")
editor.write("notes.txt", "saved from Lua\n")
return function(engine, editor)
    -- Called once per frame. editor.openEditor() returns to editing.
end
```

The default environment inherits available game globals. `e` and `engine` refer
to the game engine; `print` appears in the editor output. The game's own save
directory is added to `package.path` for plain Lua modules.

The optional **Guard** limits Lua instructions around user chunks/callbacks.
It is initially on. Native calls may not be interruptible, and a program that
replaces event handlers or changes the UI may require reloading an editor slot.
User Lua can bypass normal storage protections. Keep working recovery entries
and your external backup.
