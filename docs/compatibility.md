# Compatibility and transfer evidence

The tested reference is **Seedsow Lullaby demo 1.0.0 downloaded from the US
eShop**, with console results on Switch 1 and Switch 2. That does not establish
that a US copy is required. Region, edition, version, title ID and save layout
are different facts; matching a name or ID alone is not a successful editor test.

**Community reports, added 2026-10-27:** working cases have also been reported
for the **Japanese demo**, **UK demo** and **US full game**. These are user
reports, separate from the project's own reference testing. Exact game versions,
console/firmware combinations, transfer steps and feature coverage were not
recorded, and the maintainer has not independently reproduced these cases.

## Compatibility status

| Status | Configuration | Evidence or limit |
| --- | --- | --- |
| Hardware tested | Reference demo on Switch 1 and Switch 2 | Manual editing, wired-keyboard input, saving/publishing, full game restart and reload, and the original Pi controller-upload path worked. |
| Reported working by users | Japanese demo | Working case reported as of 2026-10-27; exact version and feature coverage not recorded. Not independently reproduced by the maintainer. |
| Reported working by users | UK demo | Working case reported as of 2026-10-27; exact version and feature coverage not recorded. Not independently reproduced by the maintainer. |
| Reported working by users | US full game | Working case reported as of 2026-10-27; exact version and feature coverage not recorded. Not independently reproduced by the maintainer. |
| Plausible, untested | Other regional demos, full-game editions and versions without reports | No region-exclusive requirement has been shown. A related engine or matching catalog entry alone does not prove save compatibility. |
| Locally tested, hardware pending | Current Windows/Pi packaging and alongside-editor updates | Regression/GUI/packaging checks do not replace a fresh console/Pi installation trial. |
| Cannot perform the restore step | Stock Switch 1 or Switch 2 alone | This route uses homebrew JKSV on Switch 1 to restore the prepared save. |
| Cannot perform the official transfer while blocked | Source banned from required services, Nintendo servers blocked, or isolated emuMMC without Nintendo access | Connectivity and account verification are required at transfer time. This says nothing about an editor already installed. |

**No additional game edition is established as incompatible.** Untested is not
the same as known broken. Windows/Pi are the implemented optional uploader;
controller/grid or wired-keyboard use on the console needs neither.

## Nintendo Account and networking

The source and destination **save users** must be linked to the same Nintendo
Account for the documented individual-game transfer. This is not inherently a
requirement to download the demo through that account. The intended save users
must be able to launch the installed software.

Nintendo documents internet connectivity and current system software for save
transfer. Blocking Nintendo servers beforehand can prevent transfer, even though
the save moves between nearby consoles. Check any update prompt before choosing
to proceed; this project does not guarantee future transfer availability.
See [Nintendo's individual-save transfer requirements](https://www.nintendo.com/sg/support/switch/secondary/transfer.html).

The documented route uses online-capable **sysNAND/sysMMC** because it needs
Nintendo connectivity and account verification. An isolated **emuMMC** normally
blocks Nintendo servers and cannot complete the transfer in that state. These
environments have separate saves. This does not mean the transfer feature has a
technical physical-NAND requirement. Using CFW on sysNAND is not ban-proof.

After installation, editing, saving, running Lua and reloading after restarting
the game require no Nintendo connection. Optional uploads use a PC/Pi LAN link
and Bluetooth controller input to the console, not Nintendo services.

## Application/title IDs: research checked 2026-10-26

| Edition | Application/title ID | Basis |
| --- | --- | --- |
| Reviewed demo obtained from US eShop | `010042D022AEA000` | The reviewed starter's JKSV metadata and original project record. This is the current starter target. |
| Full game, US / UK / Japan catalog entries | `0100EE5021C9E000` | All three catalog entries report this ID. Separately, the US full game has a user-reported working case; this does not establish UK/Japanese full-game compatibility. |
| Regional demos beyond the reference | Not independently resolved | Dataset demo entries provide eShop NSU IDs and parent full-game IDs, but their own `id` fields are null. Do not substitute the parent's ID. |

Source: [title database documentation](https://github.com/blawar/titledb), checked at
revision `d424690446eec6f4484209b9a1c067c7f7511398`:
[US catalog](https://github.com/blawar/titledb/blob/d424690446eec6f4484209b9a1c067c7f7511398/US.en.json),
[UK catalog](https://github.com/blawar/titledb/blob/d424690446eec6f4484209b9a1c067c7f7511398/GB.en.json),
[Japan catalog](https://github.com/blawar/titledb/blob/d424690446eec6f4484209b9a1c067c7f7511398/JP.ja.json).
The recorded demo **NSU IDs** are `70030000022768`, `70030000022769` and
`70030000022770`, respectively. NSU IDs identify storefront entries; they are
not save application IDs. This third-party catalog is not a complete compatibility
survey or a substitute for inspecting the intended title's own backup.
The community reports above do not independently verify additional title IDs or
change the reviewed starter's metadata target.

## Supporting another target

The general [metadata helper](../tools/README.md#portable-jksv-metadata) takes explicit
application ID, owner ID and save/journal sizes. It contains no starter title ID.
The general compatible-save builder retains the supplied backup's metadata.

For another edition, inspect its own JKSV backup metadata, verify the native
save layout and launcher behavior, test restore and full restart on hardware,
then review a separate release target. Changing metadata alone does not convert
a demo save into a full-game save or demonstrate compatibility. The
[original starter infrastructure](../maintainer/README.md) deliberately retains
its original target and exact validation hashes.
