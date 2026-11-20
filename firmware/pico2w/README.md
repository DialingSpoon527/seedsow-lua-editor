# Pico 2 W wired controller firmware

Use [switch-pico2w-uart.uf2](switch-pico2w-uart.uf2) on a **Raspberry Pi Pico 2 W**.
Follow the [Pico setup guide](../../docs/07-pico-upload.md) for flashing, wiring,
testing, calibration and sending the uploader. A 3.3 V USB-to-UART adapter is
required. Wi-Fi and Bluetooth are unused. This exposes one USB controller.

This is an unmodified source build of jyapayne/switch-pico at
`02ff001ca206997229766256af0d0a096e26fb39`, configured for the Pico 2 W instead
of the default RP2040 Pico. The PC sender's UART v3 reports are unchanged.
The source is [available at the pinned revision](https://github.com/jyapayne/switch-pico/tree/02ff001ca206997229766256af0d0a096e26fb39).

Compilation and Raspberry Pi picotool inspection passed: board `pico2_w`,
RP2350, ARM Secure image, SDK 2.2.0. **No physical Pico or console test has
been performed.** A successful build does not confirm button delivery.
The [build record](build.json) identifies the binary and configuration.
Run `py tools/check_pico2w_firmware.py` from the installer folder to check it.

## Rebuild from source

These instructions are for someone building firmware; users can use the UF2
above. Install Git, Python 3, native CMake, Ninja, Arm GNU Toolchain 14.2.Rel1
for `arm-none-eabi`, and Raspberry Pi picotool 2.2.0-a4 first.
Use [Arm's official toolchain](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads)
and [Raspberry Pi's picotool binaries](https://github.com/raspberrypi/pico-sdk-tools/releases/tag/v2.2.0-2).
Put the tools on PATH in your build terminal. Use a fresh working directory.

Run these commands one at a time:

```text
git clone https://github.com/jyapayne/switch-pico.git switch-pico
git -C switch-pico checkout 02ff001ca206997229766256af0d0a096e26fb39
git clone https://github.com/raspberrypi/pico-sdk.git pico-sdk
git -C pico-sdk checkout a1438dff1d38bd9c65dbd693f0e5db4b9ae91779
git -C pico-sdk submodule update --init lib/tinyusb
```

Replace `SDK_PATH`, `ARM_TOOLCHAIN_PATH`, and `PICOTOOL_CMAKE_PATH` below with
absolute paths. The toolchain path contains `bin/arm-none-eabi-gcc`; the
picotool path contains `picotoolConfig.cmake`. Keep quotes around paths.
This command is one line:

```text
cmake -S switch-pico -B build-pico2w -G Ninja -DPICO_BOARD=pico2_w -DPICO_PLATFORM=rp2350-arm-s -DSWITCH_PICO_INPUT_BACKEND=UART -DSWITCH_PICO_UART_CONTROLLERS=1 -DSWITCH_PICO_SYS_CLOCK_MHZ=150 -DCMAKE_BUILD_TYPE=Release "-DPICO_SDK_PATH=SDK_PATH" "-DPICO_TOOLCHAIN_PATH=ARM_TOOLCHAIN_PATH" "-Dpicotool_DIR=PICOTOOL_CMAKE_PATH"
cmake --build build-pico2w --parallel 4
picotool info -a build-pico2w/switch-pico.uf2
```

SDK warnings about missing wireless dependencies are expected for this UART
build. Check the final image says `pico2_w`, RP2350 and ARM Secure. Rename a
copy of `build-pico2w/switch-pico.uf2` to `switch-pico2w-uart.uf2` for packaging.
Build dates/tool versions can change the checksum; the recorded checksum
identifies the included build, rather than guaranteeing bit-for-bit rebuilds.
The packaged build also used GCC's `-ffile-prefix-map` in C/C++ flags to replace
local workspace paths with `/workspace` in diagnostic strings. When adding
that option, preserve the SDK's Cortex-M33 flags (`-mcpu=cortex-m33 -mthumb
-march=armv8-m.main+fp+dsp -mfloat-abi=softfp -mcmse`); replacing them can select
the wrong CPU configuration. Local account names are absent from the image.
None of these commands flashes a device.

## Notices

This binary retains its component licenses. Keep the `licenses/` directory
beside it when redistributing:

- switch-pico: MIT, Joey Yakimowich-Payne.
- Switch Pro driver/descriptors derived from GP2040-CE: MIT, OpenStickCommunity
  and Jason Skuby; upstream source retains the attribution comments.
- Pico SDK: BSD-3-Clause, Raspberry Pi (Trading) Ltd.
- TinyUSB: MIT, Ha Thach.
- Arm compiler runtime: GCC GPLv3 with the GCC Runtime Library Exception.
- Newlib: component-specific notices in `licenses/NEWLIB-NOTICES.txt`.

Bluepad32, BTstack, CYW43 Wi-Fi/Bluetooth firmware, and the upstream Wii/native
controller experimental backends are not linked into this UART build.
