# Enter the small uploader by hand

Complete [existing-editor setup](02-existing-editor.md#2-generate-your-uploader)
first. You should have a generated `build/VIEW_TYPING_SHEET.html` and two chosen
free slots. This route needs no Pi.

You will enter roughly **3,700 characters**, divided into about 120 small entries.
The exact count depends on your settings and is printed on your sheet. The
console's keyboard dialog accepts **32 characters per entry**; the complete Lua
program can be much longer.

## 1. Prepare an empty program

1. Load the editor, normally through **slot 1**.
2. Select **Choose slot** and enter your chosen **uploader slot**. This must be
   different from the destination reserved for Alula's launcher. Confirm that
   it does not contain a program you want to keep.
3. Select **File / new**, enter a new filename such as `artemis-uploader.lua`,
   then confirm. If this filename already exists, choose another new name.
4. Check that the buffer is empty and shows **0 bytes**. Opening an unused slot
   can initially create a Hello World example; opening a new filename gives you
   the empty buffer needed here. If the editor asks you to repeat an action to
   discard that example, do so once you have checked it is the default example.
5. Use **TEXT** mode. Leave the cursor at the end, initially byte **0**.

## 2. Type the sheet in order

1. On your computer, open **build/VIEW_TYPING_SHEET.html** in a browser. Windows
   setup opens it automatically. You can use `TYPE_IN_ORDER.txt` instead.
2. Start at **row 001**. Select **Keyboard +** in the console editor.
3. Type only that row's code. In the text sheet, that means the characters to
   the right of `|`, without the separator space or row number. Match punctuation,
   capitalization, quotes and backslashes exactly.
4. Confirm the keyboard dialog. The cursor advances to the end of the inserted
   text. Tick the row on the computer's sheet.
5. Open **Keyboard +** again for the next row, continuing in order. The next
   entry goes immediately after the previous entry. **Do not add a newline or
   a space between rows.** Spaces already printed inside a row belong to the code.
6. Use **Save file** periodically to keep your work. Write down the last row
   completed if you take a break; the HTML checkboxes are not saved across page
   reloads. Resume at the first untyped row, with the cursor at the buffer's end.

A wired USB keyboard can type into the same system dialog and is usually easier
for punctuation. You still confirm each entry before opening the next dialog.
The controller-operated keyboard also works. There is no need to use the editor's
character grid unless you prefer it for a particular character.

**Keyboard +** inserts text. **Edit line** replaces a segment; use Keyboard + for
this procedure. If you move the cursor accidentally, use **Byte offset** and enter
the current total byte count to place it at the end before continuing.

The first three rows contain the generated computer address, launcher slot and
TCP port. The sheet already filled these in. `uploader/r14_body.lua` is the
compact body without those settings; type from your generated sheet.

## 3. Check and publish

1. After the last row, compare the editor's byte count with **Expected final
   byte count** on the sheet. The source is ASCII, so bytes and characters match.
   A matching length catches omissions or extras, but does not prove every
   character was typed correctly.
2. If the count is wrong, use your saved row notes and compare the text. **Undo**
   can remove a recent mistaken edit while it remains in the editor's undo history.
   Fix the source before running it; a native uploader typo can crash the game.
3. Confirm the selected slot is still your **uploader slot**, then choose
   **Save + publish**. Keep the launcher destination empty for the installer.

Return to [start the computer sender](02-existing-editor.md#3-start-the-computer-sender-then-the-uploader).
Wait for its **Listening** message before choosing **RUN buffer** on the console.
