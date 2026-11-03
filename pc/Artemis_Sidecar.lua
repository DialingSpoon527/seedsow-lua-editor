-- Artemis sidecar: launched manually from an existing Seedsow editor user slot.
-- Recovery: hold MINUS while loading this slot to ignore ax_inject2.lua.
-- Does NOT alter the game's automatic startup or numbered editor saves.
if debug and debug.sethook then debug.sethook() end
editor.screen('0xff000000')
return function(eng)
 if debug and debug.sethook then debug.sethook() end
 _G.e=eng
 local recovery=eng:isDown(114)
 _G.n2h_was_recovery=recovery
 local path='save:/ax_inject.lua'
 if not recovery and eng:isFileExists('save:/ax_inject2.lua') then
  path='save:/ax_inject2.lua'
 end
 eng:include(path)
end
