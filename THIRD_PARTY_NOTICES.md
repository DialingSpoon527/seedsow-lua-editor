# Third-party notices

The project's 0BSD license and no-credit permission apply to project-owned code
and documentation, including earlier revisions. They do not relicense the
third-party components, game content or other material described below.

The Pi bridge uses [NXBT](https://github.com/Brikwerk/nxbt), copyright Reece Walsh
and contributors, under the MIT license. The installer downloads the pinned
revision `ec4b800ad6c55de96bb6c7f9f84b5bdc59a4c975` and applies the controller
compatibility fixes in `pi/patch_nxbt.py`. Its license is reproduced in
[licenses/NXBT-MIT.txt](licenses/NXBT-MIT.txt) and installed beside the downloaded
library. NXBT source is not bundled in this source release.

Python/Tk, BlueZ, D-Bus and the operating-system packages remain separately
installed dependencies under their respective licenses. Lupa is an optional
development dependency and is not bundled.

Seedsow Lullaby and its game engine belong to their respective owners. This
source-code ZIP includes no game dump or save backup. A separate ready-to-restore
starter save includes the editor and example programs, with personal account
identifiers and personal files excluded. Its portable JKSV metadata contains
the public game attributes and blank personal fields. This project
is an independent tool and is not affiliated with the game publisher or Nintendo.
