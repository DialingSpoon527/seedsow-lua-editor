-- Ordinary own-save files. Protection is an editor policy, not a Lua sandbox.
local W = {limit=1048576}
function W.valid(name)
    return type(name)=='string' and #name>0 and #name<=80 and name:match('^[%w_][%w_.%-]*$')~=nil
end
function W.protected(name)
    if not W.valid(name) then return true end
    local n=name:lower()
    if W.private_prefix and n:sub(1,#W.private_prefix)==W.private_prefix then return true end
    if n=='saveg.dat' or n:match('^save000[123][%.]') then return true end
    for _,prefix in ipairs({'ssedit','ssseed','ssboot','ssethumb','sed01.','sed02.','sed03.'}) do
        if n:sub(1,#prefix)==prefix then return true end
    end
    return n:match('^ss%d%d%d%.asb')~=nil
end
function W.read(base,name)
    assert(W.valid(name),'Use a plain own-save filename (letters, digits, _, -, .).')
    local f,why=io.open(base..'/'..name,'rb')
    if not f then return nil,why end
    local ok,data=pcall(function() return f:read(W.limit+1) or '' end)
    pcall(function() f:close() end)
    if not ok then return nil,tostring(data) end
    if #data>W.limit then return nil,'File exceeds the 1 MiB editor limit; nothing was truncated.' end
    return data
end
function W.put(base,name,data)
    assert(W.valid(name),'Invalid filename')
    local n=name:lower()
    if W.recovery_readonly and (n=='saveg.dat' or n:sub(1,6)=='ssedit'
        or n:match('^save000[123]%.') or n:match('^sed0[123]%.asb')
        or n:match('^ssboot[123]%.bin') or n:match('^ssseed00[123]%.bin')) then
        return false,'Original V3 recovery file is read-only in this editor'
    end
    assert(type(data)=='string' and #data<=W.limit,'File exceeds editor limit')
    local f,why=io.open(base..'/'..name,'wb')
    if not f then return false,tostring(why) end
    local ok,err=pcall(function()
        assert(f:write(data)); assert(f:flush()); assert(f:close())
    end)
    if not ok then pcall(function() f:close() end); return false,tostring(err) end
    local back,readerr=W.read(base,name)
    if back~=data then return false,readerr or 'Readback mismatch' end
    return true
end
function W.save(base,name,data,internal)
    if not W.valid(name) then return false,'Invalid filename' end
    if #name>72 then return false,'Writable filenames are limited to 72 characters to leave room for recovery suffixes.' end
    if not internal and W.protected(name) then return false,'Protected editor/launcher file; choose a user filename.' end
    if #data>W.limit then return false,'File exceeds editor limit' end
    local old,why=W.read(base,name)
    if old==nil then
        -- Distinguish an absent file from a readable file larger than the limit.
        local f=io.open(base..'/'..name,'rb')
        if f then f:close(); return false,why or 'Cannot safely back up existing file' end
    end
    local ok,err=W.put(base,name..'.new',data)
    if not ok then return false,'Staging: '..tostring(err) end
    if old~=nil then
        ok,err=W.put(base,name..'.bak',old)
        if not ok then return false,'Backup: '..tostring(err) end
    end
    ok,err=W.put(base,name,data)
    if not ok then return false,'Target write: '..tostring(err)..'; previous .bak and staged .new retained.' end
    return true
end
function W.splice(data,offset,remove,insert)
    assert(type(offset)=='number' and offset%1==0 and offset>=0 and offset<=#data,'Offset outside file')
    assert(type(remove)=='number' and remove%1==0 and remove>=0 and offset+remove<=#data,'Range outside file')
    assert(#data-remove+#insert<=W.limit,'File exceeds editor limit')
    return data:sub(1,offset)..insert..data:sub(offset+remove+1),offset+#insert
end
function W.unhex(text)
    local clean=text:gsub('%s','')
    assert(not clean:find('[^%da-fA-F]'),'Hex accepts only 0-9, A-F and whitespace')
    assert(#clean%2==0,'Hex needs two digits per byte')
    assert(#clean/2<=W.limit,'Hex exceeds editor limit')
    return (clean:gsub('..',function(pair) return string.char(tonumber(pair,16)) end))
end
function W.hex(data)
    return (data:gsub('.',function(c) return string.format('%02X',c:byte()) end))
end
function W.adler(data)
    local a,b=1,0
    for i=1,#data do a=(a+data:byte(i))%65521; b=(b+a)%65521 end
    return b*65536+a
end
function W.u32(n)
    return string.char(n%256,math.floor(n/256)%256,math.floor(n/65536)%256,math.floor(n/16777216)%256)
end
function W.asb(commands)
    local function text(s) return W.u32(#s)..s..'\0' end
    local out={'ASB\0\0',W.u32(#commands)}
    for line,command in ipairs(commands) do
        local keys={}; for k in pairs(command[2]) do keys[#keys+1]=k end; table.sort(keys)
        out[#out+1]=W.u32(0)..text(command[1])..W.u32(line)..W.u32(#keys)
        for _,key in ipairs(keys) do out[#out+1]=text(key)..text(command[2][key]) end
    end
    return table.concat(out)
end
return W
