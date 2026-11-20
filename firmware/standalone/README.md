# Standalone Pico 2 W sender

Start with [the user guide](../../docs/09-pico2w-standalone.md). The included
`pico2w-standalone-TEMPLATE.uf2` is intentionally unconfigured. The setup tool
creates a private configured UF2 without requiring a compiler or UART adapter.
Do not flash the template expecting it to send a file.

## Implementation and evidence

- One USB Switch Pro controller, using the pinned switch-pico USB driver.
- New `main.cpp` replaces upstream's UART application loop. No UART input,
  Wi-Fi or Bluetooth connection is used.
- The 8 KiB configuration object contains a 16-byte marker, little-endian
  packet length and CRC32, then the existing SSE2 packet. Firmware checks CRC32,
  SSE2 header, destination slot, size and source Adler-32 before allowing upload.
- BOOTSEL is sampled using upstream's flash-safe RP2350 sampler. Actions occur
  on release after a five-second startup guard. No automatic input on insertion.
- Short / two-second / five-second holds choose L+R then A test / calibration / upload.
  A press while active cancels and locks until power-cycle. A file upload starts
  at most once per power-on. The firmware cannot inspect the console screen.
- `engine.c` holds each button phase until USB has actually reported it, then
  for at least 100 ms setup / 200 ms edge hold. USB loss or a reporting stall
  aborts with neutral controls. The receiver still has to confirm saving.
- Native tests compile the **actual C engine** into a local DLL and reconstruct
  the file from its R-clock edges, check calibration, cancellation/stall release,
  idle/overlap prevention, gesture thresholds, L+R registration, malformed packets
  and CRC32. Configurator tests check reserved-area-only
  changes, wrong-chip images, truncation, oversize and repeat configuration.

Compilation and offline tests are evidence of those checks only. No Pico has
been flashed and no console transfer has been tested for this build.
`template.json` pins the included template checksum and source revisions.

## Rebuilding

Use the pinned SDK, TinyUSB, Arm 14.2.Rel1 compiler, Ninja and picotool from the
[UART build instructions](../pico2w/README.md#rebuild-from-source). Instead of
configuring switch-pico directly, configure **this folder**, passing
`SWITCH_PICO_SOURCE` as the absolute path of the pinned switch-pico checkout:

```text
cmake -S firmware/standalone -B build/standalone-compile -G Ninja "-DSWITCH_PICO_SOURCE=UPSTREAM_PATH" "-DPICO_SDK_PATH=SDK_PATH" "-DPICO_TOOLCHAIN_PATH=ARM_TOOLCHAIN_PATH" "-Dpicotool_DIR=PICOTOOL_CMAKE_PATH" -DCMAKE_BUILD_TYPE=Release
cmake --build build/standalone-compile --parallel 4
picotool info -a build/standalone-compile/upstream/switch-pico.uf2
```

Board `pico2_w`, platform `rp2350-arm-s`, stock 150 MHz clock, UART backend USB
driver and one controller are selected by the wrapper. It removes only upstream
`main.cpp`, adding this application's main/engine and the original BOOTSEL sampler.
Dependencies are separate, unchanged source checkouts. The packaged build uses
the same compiler versions as the UART image, with local paths remapped to
`/workspace` by GCC's `-ffile-prefix-map`, preserving the Cortex-M33 flags.
No flashing command is part of this build recipe. Update the template manifest
after a reviewed rebuild; build dates can change its binary checksum.

For the native engine test, use a native C compiler (for example Zig):

```text
zig cc -shared -O2 firmware/standalone/engine.c -o build/standalone-engine.dll
python tests/standalone_engine_checks.py build/standalone-engine.dll
python -m unittest discover -s tests
```

## Licenses

New application code/configurator uses the project's 0BSD license. The binary
also retains switch-pico, GP2040-CE, Pico SDK, TinyUSB and compiler/C-runtime
notices in [the adjacent license directory](../pico2w/licenses/).
The upstream BOOTSEL sampling code additionally credits awalol/DS5Dongle under
MIT; retain `DS5Dongle-MIT.txt` here. Its source comments are preserved in the
unchanged pinned upstream file. This does not include Bluepad32, BTstack or
wireless firmware. Distribute this folder with the adjacent dependency notices.
