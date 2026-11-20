# Method 1 — type the uploader

Start after [preparing your computer and editor](02-existing-editor.md). Have your uploader slot number, Artemis slot number, and generated typing sheet beside you.

You can type with the controller’s on-screen keyboard or a wired USB keyboard. The same steps work for either. Expect about **3,700 characters**, entered in small pieces. Your sheet gives the exact length.

If you have a modded Switch 1, [RealRobertBrownieJr’s Plume USB guide](https://github.com/RealRobertBrownieJr/seedsow-artemis-plume-installer) provides another text-entry option. It uses the Switch 1 as a USB keyboard to send numbered uploader chunks. Check its connection settings against your own setup before using those files.

## 1. Open an empty file

1. Load your ordinary Lua Editor, normally slot 1.
2. Select **Choose slot** and enter your **uploader slot**. Leave the Artemis destination empty.
3. Select **File / new**. Enter a new filename such as `artemis-uploader.lua`.
4. If that filename already exists, choose a different new name.
5. Check that the buffer says **0 bytes**. An empty slot can initially create a Hello World example. The new filename gives you the empty file needed here. If asked to repeat an action to discard changes, first confirm that you are discarding only that new default example.
6. Select **TEXT** mode.

## 2. Type each row

1. On the computer, double-click **build/VIEW_TYPING_SHEET.html**. It opens in your browser.
2. Find row **001**.
3. On the console, select **Keyboard +**.
4. Type exactly the code in row 001. Include its punctuation and capitalization. Leave out the row number and checkbox.
5. Confirm the keyboard dialog on the console. The code is inserted and the cursor moves forward.
6. Tick row 001 on your computer.
7. Select **Keyboard +** again and enter row 002.
8. Continue in order until every row is entered. Put each entry immediately after the previous one. Add no spaces or newlines between rows. Spaces printed inside a row are part of that row’s code.

The system keyboard accepts up to **32 characters per entry**. The generated sheet already fits that limit. **Keyboard +** inserts text. **Edit line** replaces text, so use **Keyboard +** for these steps.

Select **Save file** periodically. Before taking a break, write down the last completed row. Browser checkboxes disappear if you refresh or close the page. When resuming, put the cursor at the end of your existing text. **Byte offset** can move it there using the current total byte count.

## 3. Check the result

1. Compare the console’s byte count with the sheet’s **Expected final byte count**.
2. If they differ, check your row notes and correct the text before running it.
3. A matching count can still hide a wrong character. Check quotes, backslashes, punctuation, and the first three settings rows carefully.
4. Confirm that **Choose slot** still shows your uploader slot.
5. Select **Save + publish**.

The uploader is now saved. Continue with [Install and open Artemis](08-finish-installation.md). Start the computer sender and wait for **Listening** before running the console uploader.
