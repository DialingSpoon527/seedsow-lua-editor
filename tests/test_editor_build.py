"""Exercise update reconstruction with Lua's actual string and newline rules."""
import sys
import unittest
import zlib
from pathlib import Path

from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'editor'))
from build_side_editor import isolated_source, payload


class UpdateReconstruction(unittest.TestCase):
    def reconstruct(self, base, candidate):
        source = isolated_source(candidate, 30)
        lua = LuaRuntime(encoding=None)
        lua.globals()[b'base'] = base
        lua.globals()[b'adler'] = zlib.adler32
        lua.execute(b'''
            local state={slot=30,guard=true,config={},source=base}
            seedsow_editor={
                test_state=function() return state end,
                storage={read=function() return base end,adler=adler}
            }
            engine={var=function() return 'save:' end}
        ''')
        update = lua.execute(payload(base, source, 30, 'test-build'))
        update(lua.globals()[b'engine'])
        self.assertEqual(lua.globals()[b'reconstructed'], source)

    def test_delta_preserves_literal_delimiters_and_placeholder_text(self):
        candidate = b'''-- SOURCE_SIZE SOURCE_CRC BUILD_ID SIDE_SLOT PATCH_DATA
-- closing delimiters: ]=] ]==] ]===]
return {start=function(engine,config,source) reconstructed=source end}
'''
        self.reconstruct(b'-- a retained line\n'+candidate, candidate)

    def test_windows_newlines_and_missing_final_newline(self):
        self.reconstruct(b'-- base\n', b'\r\n-- Windows\r\nreturn {start=function(e,c,s) reconstructed=s end}')

    def test_invalid_update_slots_are_rejected(self):
        for slot in (True, False, 3, 121, 30.5, '30'):
            with self.subTest(slot=slot), self.assertRaises(ValueError):
                isolated_source(b'', slot)


if __name__ == '__main__':
    unittest.main()
