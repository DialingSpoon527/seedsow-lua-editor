# Code cleanup review — 2026-10-27

## Changes

- **UI layout:** navigation uses a full toolbar row with 32-pixel text areas.
  The prior 25-pixel areas were shorter than the working toolbar and are a
  likely explanation for missing labels. The current fresh-save build was
  reported working on console on 2026-10-27; detailed feature coverage was not
  recorded. Tests inspect emitted font sizes and layer geometry, not only hits.
- **Font caching:** cache the complete font geometry. Calibration reused preview
  layer IDs with different sizes, so caching only the ID left stale dimensions
  when returning to editing.
- **Fresh saves:** compose the current runtime in slots 1-3 and all program
  launchers. Alongside updates share the same Lua modules. The frozen V3 file is
  only a compatibility baseline for older installations and validation.
- **Input:** remove a second, unused set of controller fallbacks and avoid
  polling default face-button aliases before immediately replacing the result.
  Clear old native handlers while keeping harmless stale callbacks inert.
- **PC worker state:** a Pi/network error no longer clears another operation's
  build flag. Only that build's completion or failure callback releases it.
- **Unused code/data:** remove the unused keyboard-transfer wrapper, unused PC
  version constant, duplicate NXBT pin constant and empty source-hash field.
- **Tests and packaging:** use one native-save installer for private and public
  builds; check current public assets against canonical reconstruction and the
  historical native validator. Rename transfer tests by purpose, support backup
  folder wrappers in update checks, and test the selected update slot.
- **Wording:** remove directional button explanations and repetitive scroll
  notifications. Keep physical shortcuts in the footer. Label the PC sample
  action as an example and document actual update methods.

## Deliberate behavior retained

- The Switch system keyboard is hardcoded to 32 characters in the tested game.
  `textfieldsize` truncates returned text; it does not set the keyboard maximum.
  Direct USB character input is not exposed by this Switch build. Native keyboard
  behavior was left unchanged; the docs and recording engine now reflect the cap.
- Learned controller profiles take precedence over standard aliases because
  translated hardware mappings can differ, including swapped X/Y aliases.
- The event filter and no-op legacy callback prevent duplicate native/game input
  from operating the editor while its current input path polls held buttons.
- Staging, backups and readback verification protect file writes; failure tests
  demonstrate that these steps have different jobs.
- Random example IDs distinguish a newly uploaded program from an older one.
- The controller backend field remains in the LAN protocol for existing clients.
  There is currently one implemented upload backend.
- The pinned NXBT version, continuous-report fixes and timing margin have hardware
  history. Removing them without another trial would be speculative.
- Future-proofing messaging and the SmileBASIC note remain intentional positioning.

The historical first-publication force-push option is retained pending a
maintainer decision. Routine releases use ordinary pushes or tagged CI.

## Validation limits

Lua tests use a recording engine and simulated native serialization/commits.
The optional layout renderer uses a substitute host font. Neither establishes
native rendering behavior. The user reported that the delivered fresh-save build
works on console on 2026-10-27. This is a hardware report with unspecified feature
coverage, not evidence that every navigation, keyboard, publication, restart or
recovery path was tested. Fresh PC/Pi installation and alongside-update hardware
trials remain pending.
