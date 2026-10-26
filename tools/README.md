# General-purpose save tools

These tools help inspect, edit or build **compatible saves**. They are not needed
to install the [already-built editor save](../docs/01-console-install.md), and
they do not enforce the original public starter's exact hashes.

| Tool | Purpose |
| --- | --- |
| [`../editor/build.py`](../editor/build.py) | Build a private editor installation from an owner's compatible backup; rebuild existing editor saves while retaining user files. |
| [`../editor/build_side_editor.py`](../editor/build_side_editor.py) | Build an alongside-editor Lua update for a fresh slot using the installed recovery base. |
| [`indexed_save.py`](indexed_save.py) | Decode and edit indexed native saves, with expected-byte checks and relocation of affected offsets. |
| [`asb.py`](asb.py) | Encode/decode ASB version-0 script records. |
| [`save_globals.py`](save_globals.py) | Read length-prefixed global variables and replace a fixed-width embedded title while checking the layout. |
| [`jksv_metadata.py`](jksv_metadata.py) | Generate portable JKSV metadata for an explicitly described account-save target. |

See [general development](../docs/06-development.md) for builder commands,
input/output expectations, regression checks and the runtime source layout.
These modules are shared by builders, tests and maintainer scripts; there are
no copied parsers or hidden dependencies on the reviewed starter packager.

## Portable JKSV metadata

From the repository root, an explicit target can be described with:

```python
from tools.jksv_metadata import portable_account_metadata

metadata = portable_account_metadata(
    application_id=target_application_id,
    owner_id=target_save_owner_id,
    data_size=target_data_size,
    journal_size=target_journal_size,
)
```

The four `target_*` values must come from the intended title's own metadata;
the helper supplies no game, region or size defaults. It emits the standard
account-save layout (type 1, rank/index/flags 0, user space 1) with account UID,
timestamp and commit ID blanked. Nonstandard attributes need separate review.
It does not alter game contents or establish compatibility.

The layout follows [JKSV's metadata structure](https://github.com/J-D-K/JKSV/blob/rewrite/include/fs/SaveMetaData.hpp).
[JKSV's existing-save processing](https://github.com/J-D-K/JKSV/blob/rewrite/source/fs/SaveMetaData.cpp)
uses the selected target save and the recorded data/journal sizes. This is why
target metadata and native save compatibility must be assessed separately.

Exact original starter hashes, privacy allowlists, source ZIP packaging and
GitHub publication live in [`../maintainer/`](../maintainer/README.md).
