# Third-party notices

The [0BSD license](LICENSE) applies to project-owned code and documentation. It
does not relicense Alula's code, the native payload's upstream contributions,
fonts, game material or dependencies. The original source handoff did not supply
a separate authorship/license inventory for the compact bootstrap; retain its
provenance and upstream attribution when redistributing it.

This installer adapts code downloaded from
[Alula's switch-artemis-launcher](https://github.com/alula/switch-artemis-launcher/),
specifically the v1 `seedsow_save.zip`. That project credits
[n0llptr/remote_lua_loader](https://github.com/n0llptr/remote_lua_loader),
[Gezine/ArtemisLuaLoader](https://github.com/Gezine/ArtemisLuaLoader) and
**Proggy Clean TT by Tristan Grimmer**. Consult upstream for the terms applying
to those materials. This repository does not bundle Alula's ZIP or font.

The Pi route includes modified bridge, pairing-agent, installer, and connection
export code retained from this project’s 0.1.3 companion under its 0BSD license.
The desktop companion remains a separate download. The Pi installer fetches
[NXBT](https://github.com/Brikwerk/nxbt) at revision
`ec4b800ad6c55de96bb6c7f9f84b5bdc59a4c975` and applies the local compatibility
patches. NXBT’s MIT notice is retained in [licenses/NXBT-MIT.txt](licenses/NXBT-MIT.txt)
and installed beside the downloaded library. Its source is not bundled here.

Python, Tk, operating-system packages and JKSV remain separate dependencies.
Seedsow Lullaby, its engine and Nintendo software belong to their respective
owners. This is an independent project.

## Controller transfer support

`pc/controller_protocol.py` is retained from this project’s 0.1.3 companion,
under its 0BSD license. It defines the existing SSE2 receiver packet and button
symbols. `pc/send_controller.py` implements transport through an HTTP controller
bridge or a serial adapter.

The wired serial backend targets [jyapayne/switch-pico](https://github.com/jyapayne/switch-pico)
at revision `02ff001ca206997229766256af0d0a096e26fb39`, using the documented
UART v3 report format. Its firmware, SDK dependencies, and upstream Python
package remain separate downloads with their own licenses. No firmware source
or binary is bundled here. pyserial 3.5 is an optional dependency for the wired
path and is distributed under its own BSD license.
