-- Standard game input aliases for ordinary editing; upload calibration is separate.
local Controls={}
Controls.__index=Controls
local defaults={A={258,13},B={257,27},X={259,112},Y={256,113},L={260,116},R={261,117}}
local buttons={CLICK='A',ESC='B',F1='X',F2='Y',F5='L',F6='R'}
function Controls.new(engine,definitions)
    local self=setmetatable({engine=engine,keys={}},Controls)
    local seen={}
    local function add(name,code)
        if not name or not code or code<=1 or code>350 then return end
        seen[name]=seen[name] or {}
        if not seen[name][code] then
            self.keys[name]=self.keys[name] or {}
            self.keys[name][#self.keys[name]+1]=code;seen[name][code]=true
        end
    end
    for name,keys in pairs(defaults) do for _,code in ipairs(keys) do add(name,code) end end
    for code,row in pairs(definitions or {}) do
        if type(row)=='table' then add(buttons[row.btn],tonumber(code)) end
    end
    return self
end
function Controls:held(name)
    for _,code in ipairs(self.keys[name] or {}) do
        local ok,value=pcall(function() return self.engine:isDown(code) end)
        if ok and (value==true or value==1) then return true end
    end
    return false
end
return Controls
