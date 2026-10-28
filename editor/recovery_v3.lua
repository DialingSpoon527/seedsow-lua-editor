local W=(function()
-- Ordinary own-save files. Protection is an editor policy, not a Lua sandbox.
local W = {limit=1048576}
function W.valid(name)
    return type(name)=='string' and #name>0 and #name<=80 and name:match('^[%w_][%w_.%-]*$')~=nil
end
function W.protected(name)
    if not W.valid(name) then return true end
    local n=name:lower()
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

end)()
local Transfer=(function()
-- Framed data over controller inputs. No game networking or native bridge.
local Transfer={}
function Transfer.new()
    return {bytes={},count=0,nibble=nil,expected=nil,complete=false}
end
local function number(s,at)
    local a,b,c,d=s:byte(at,at+3)
    return a+b*256+c*65536+d*16777216
end
function Transfer.feed(r,nibble)
    assert(not r.complete,'Transfer already complete')
    assert(nibble>=0 and nibble<=15 and nibble%1==0,'Invalid input symbol')
    if r.nibble==nil then r.nibble=nibble; return end
    local byte=r.nibble*16+nibble; r.nibble=nil
    r.count=r.count+1; r.bytes[r.count]=string.char(byte)
    if r.count==14 then
        local header=table.concat(r.bytes)
        assert(header:sub(1,4)=='SSE2' and header:byte(5)==1,'Invalid header. Expected 53 53 45 32 01; got '..W.hex(header))
        r.length=number(header,6); r.checksum=number(header,10); r.name_length=header:byte(14)
        assert(r.length<=W.limit,'Program exceeds editor limit')
        assert(r.name_length>=1 and r.name_length<=72,'Invalid filename length')
        r.expected=14+r.name_length+r.length
    end
    if r.expected and r.count==r.expected then
        local packet=table.concat(r.bytes)
        r.name=packet:sub(15,14+r.name_length)
        r.source=packet:sub(15+r.name_length)
        assert(W.valid(r.name) and not W.protected(r.name),'Received filename is protected or invalid')
        assert(W.adler(r.source)==r.checksum,'Checksum mismatch: nothing saved; retry at slower speed')
        r.complete=true; r.bytes={}
    end
end
return Transfer

end)()
local Input=(function()
-- Learn physical Pi buttons from held-state APIs, including the game's aliases.
local Input={}
local names={'A','B','X','Y','L','R'}
local methods={'isDown','isPush'}
local function active(e,method,key)
 local ok,v=pcall(function() return e[method](e,key) end)
 return ok and (v==true or v==1)
end
function Input.new(e,data)
 local self={e=e,map={},frames=0,maxgap=0}
 for line in (data or ''):gmatch('[^\r\n]+') do
  local name,method,tail=line:match('^(%u) (%a+) (.+)$')
  if name and method and (method=='isDown' or method=='isPush') then
   local codes={}
   for n in tail:gmatch('%d+') do n=tonumber(n);if n<=350 then codes[#codes+1]=n end end
   if #codes>0 then self.map[name]={method=method,codes=codes} end
  end
 end
 for _,name in ipairs(names) do if not self.map[name] then self.valid=false;return setmetatable(self,{__index=Input}) end end
 self.valid=true
 return setmetatable(self,{__index=Input})
end
function Input:tick()
 local now=self.e:now()
 if self.last then self.maxgap=math.max(self.maxgap,now-self.last) end
 self.first=self.first or now;self.last=now;self.frames=self.frames+1
end
function Input:held(name)
 local row=self.map[name]
 if row then for _,key in ipairs(row.codes) do if active(self.e,row.method,key) then return true end end;return false end
 local fallback={A={258,13},B={257,27},X={259,112},Y={256,113},L={260,116},R={261,117}}
 for _,key in ipairs(fallback[name] or {}) do if active(self.e,'isDown',key) then return true end end
 return false
end
function Input:start()
 self.cal={index=1,results={},neutral=self.e:now(),armed=false,counts={},live='Waiting for all buttons to be released'}
 self.frames=0;self.first=nil;self.last=nil;self.maxgap=0
end
function Input:scan()
 local found={};local labels={}
 for _,method in ipairs(methods) do
  local codes={}
  for key=1,350 do if active(self.e,method,key) then
   local id=method..':'..key;found[id]={method=method,key=key};codes[#codes+1]=tostring(key)
  end end
  labels[#labels+1]=method..': '..(#codes>0 and table.concat(codes,',') or '-')
 end
 return found,table.concat(labels,' | ')
end
function Input:step()
 self:tick()
 local c=self.cal;if not c or c.done then return end
 local now=self.e:now();local found,live=self:scan();c.live=live
 if not c.armed then
  if next(found) then c.neutral=now
  elseif now-c.neutral>=350 then c.armed=true end
  return
 end
 if next(found) then
  c.pressed=true;c.released=nil
  for id,row in pairs(found) do
   local count=c.counts[id] or {count=0,method=row.method,key=row.key};count.count=count.count+1;c.counts[id]=count
  end
 elseif c.pressed then
  c.released=c.released or now
  if now-c.released>=350 then
   c.results[names[c.index]]=c.counts;c.index=c.index+1;c.counts={};c.pressed=false;c.released=nil
   if c.index>#names then self:finish() end
  end
 end
end
function Input:finish()
 local c=self.cal;local rows={};local report={};local map={}
 for _,name in ipairs(names) do
  local counts=c.results[name];local best,score
  local details={}
  for id,row in pairs(counts) do
   details[#details+1]=id..'='..row.count
   local unique=true
   for _,other in ipairs(names) do if other~=name and c.results[other][id] then unique=false end end
   local rank=row.count+(row.method=='isDown' and 100000 or 0)
   if unique and row.count>=2 and (not score or rank>score) then best=row;score=rank end
  end
  table.sort(details);report[#report+1]=name..' observations '..table.concat(details,' ')
  if best then
   map[name]={method=best.method,codes={best.key}}
   rows[#rows+1]=name..' '..best.method..' '..best.key
  else c.error='No unique held-state key for '..name end
 end
 c.done=true;c.report=table.concat(report,'\n')
 if not c.error then self.map=map;self.valid=true;c.serialized=table.concat(rows,'\n')..'\n' end
end
function Input:summary()
 local rows={}
 for _,name in ipairs(names) do
  local row=self.map[name];rows[#rows+1]=name..'='..(row and (row.method..':'..table.concat(row.codes,',')) or '?')
 end
 return table.concat(rows,' ')
end
function Input:timing()
 local span=self.last and self.first and self.last-self.first or 0
 return string.format('Samples %d / %.1f Hz / largest gap %d ms',self.frames,span>0 and (self.frames-1)*1000/span or 0,self.maxgap)
end
return Input

end)()
-- The builder embeds storage.lua above this file as local W.
local Editor={}
local S
local start_calibration
local ROOT='zzzzsseditor'
local PROGRAM='zzzzssprogram'
local function say(message) S.status=tostring(message); S.dirty_draw=true end
local function attempt(fn)
    local ok,a,b=pcall(fn)
    if not ok then say(a); return false,a end
    return true,a,b
end
local function text(id,x,y,width,height,size,value,color,root)
    local e=S.e; local key=(root or ROOT)..'.'..id
    e:tag{'chgmsg',id=key,layered='1'}
    if not S.fonts[key] then
        e:tag{'fontinit'}
        e:tag{'font',stack='0',face='font/roboto-regular.ttf',size=tostring(size),color=color or '0xffffff',
            left='0',top='0',width=tostring(width),height=tostring(height),align='left',overflow='1',outline='0',shadow='0',show='0',layered='1'}
        S.fonts[key]=true
    end
    e:tag{'rp'}; e:tag{'print',data=value}; e:tag{'/chgmsg'}
    e:tag{'lyprop',id=key,left=tostring(x),top=tostring(y),visible='1',alpha='255'}
end
local function log(message)
    S.output[#S.output+1]=tostring(message)
    while #S.output>24 do table.remove(S.output,1) end
    S.dirty_draw=true
end
local function exists(name)
    local ok,value=pcall(function() return S.e:isFileExists(S.base..'/'..name) end)
    return ok and (value==true or value==1)
end
local function commit()
    -- A normal native save commits ordinary IO writes too, as demonstrated by the diagnostic.
    local ok,err=pcall(function() S.e:tag{'save',file='ssedit-commit.dat'} end)
    if not ok then error('Commit request failed: '..tostring(err)) end
    S.commit_pending=false
end
local function metadata()
    assert(type(sys)=='table' and type(pluto)=='table','Game save metadata is unavailable')
    S.e:tag{'var',name='g.system',data=pluto.persist({},sys)}
    S.commit_pending=true
end
local function register(slot,title)
    sys.saveslot=sys.saveslot or {}
    sys.saveslot[slot]={file=string.format('save%04d',slot),title={text=title,en=title,ja=title,cn=title},
        text={text=title,en=title,ja=title,cn=title},com=title,date=os.time()}
    sys.saveslot.lock=sys.saveslot.lock or {}
    sys.saveslot.check=sys.saveslot.check or {}
    sys.saveslot.check[string.format('save%04d',slot)]=true
    sys.saveslot.count=math.max(tonumber(sys.saveslot.count) or 0,slot)
    if slot<=3 then sys.saveslot.lock[slot]=true end
end
local function repair()
    local repaired=0
    for i=1,3 do
        local targets={
            {string.format('ssedit%d.lua',i),S.source},
            {string.format('save%04d.dat',i),assert(W.read(S.base,string.format('ssseed%03d.bin',i)))},
            {string.format('sed%02d.asb',i),assert(W.read(S.base,string.format('ssboot%d.bin',i)))}
        }
        for _,entry in ipairs(targets) do
            if W.read(S.base,entry[1])~=entry[2] then
                local ok,err=W.put(S.base,entry[1],entry[2]); assert(ok,err); repaired=repaired+1
            end
        end
        register(i,i==1 and 'LUA EDITOR V3' or (i==2 and 'PC INPUT / CALIBRATE' or 'EDITOR BACKUP 2'))
    end
    for slot=4,S.maxslot do
        local ref=W.read(S.base,string.format('ssslot%03d.ref',slot))
        local file=ref and ref:match('^([^\r\n]+)')
        if file and W.valid(file) and not W.protected(file) and exists(string.format('save%04d.dat',slot)) then register(slot,'LUA '..slot..' / '..file) end
    end
    metadata(); commit()
    return repaired
end
local function code_name(slot) return string.format('sscode%03d.lua',slot) end
local function ref_name(slot) return string.format('ssslot%03d.ref',slot) end
local function default_source()
    return '-- Editable Lua. Save + publish, then load this numbered game slot.\nprint("Hello from Switch!")\n'
end
local function remember()
    local ok,err=W.put(S.base,'ssedit-session.txt',tostring(S.slot)..'\n'..S.filename..'\n')
    assert(ok,err); S.commit_pending=true
end
local function read_target(name,new_if_missing)
    assert(W.valid(name),'Use a plain own-save filename')
    local data,err=W.read(S.base,name)
    if data==nil and exists(name) then error(err or 'Cannot read file') end
    if data==nil and not new_if_missing then error(err or 'File not found') end
    S.filename=name; S.buffer=data or ''; S.cursor=0; S.saved=S.buffer; S.undo={}; S.hex_pending=''
    remember(); say(data and ('Opened '..name) or ('New file '..name))
end
local function open_slot(slot)
    assert(slot%1==0 and slot>=4 and slot<=S.maxslot,'User slots are 4-'..S.maxslot..'; 1-3 are protected editors')
    local ref=W.read(S.base,ref_name(slot))
    local name=ref and ref:match('^([^\r\n]+)') or code_name(slot)
    assert(W.valid(name) and not W.protected(name),'Invalid slot reference')
    S.slot=slot; read_target(name,true)
    if not exists(name) then S.buffer=default_source(); S.saved=''; S.cursor=#S.buffer end
    say('User slot '..slot..' / '..name)
end
local function edit(remove,insert)
    local old=S.buffer
    local data,cursor=W.splice(old,S.cursor,remove,insert)
    if data~=old then
        S.undo[#S.undo+1]={data=old,cursor=S.cursor}
        while #S.undo>12 do table.remove(S.undo,1) end
        S.buffer,S.cursor=data,cursor
    end
    S.dirty_draw=true
end
local function save_file()
    local ok,err=W.save(S.base,S.filename,S.buffer)
    assert(ok,err); S.saved=S.buffer; remember(); commit()
    say('Saved + readback verified: '..S.filename..' ('..#S.buffer..' bytes)')
end
local function publish()
    assert(not S.filename:lower():match('^save%d+%.dat$'),'Native save bytes can be saved as a file; publish a separate Lua source file.')
    save_file()
    local target=string.format('save%04d.dat',S.slot)
    local seed=assert(W.read(S.base,string.format('ssseed%03d.bin',S.slot)))
    local ok,err=W.save(S.base,target,seed); assert(ok,err)
    ok,err=W.save(S.base,ref_name(S.slot),S.filename..'\n'); assert(ok,err)
    local thumb=W.read(S.base,'ssethumb.png')
    if thumb then
        for _,suffix in ipairs({'.png','_s.png'}) do
            local name=string.format('save%04d',S.slot)..suffix
            if not exists(name) then local wrote,why=W.put(S.base,name,thumb); assert(wrote,why) end
        end
    end
    register(S.slot,'LUA '..S.slot..' / '..S.filename)
    sys.saveslot.cont=S.slot; sys.saveslot.last=S.slot
    sys.saveslot.page=math.floor((S.slot-1)/((init and init.save_column) or 6))+1
    metadata(); commit(); say('Published slot '..S.slot..'. After restart, load this numbered slot to run it.')
end
local function dirty_guard(key)
    if S.buffer==S.saved then return true end
    local now=S.e:now()
    if S.confirm==key and now-S.confirm_tick>=350 and now-S.confirm_tick<7000 then S.confirm=nil; return true end
    S.confirm,S.confirm_tick=key,now
    say('Unsaved edits: repeat this action after releasing the button to discard; Save file keeps them.')
    return false
end
local function guarded(fn,...)
    local args={...}
    local dh=debug and debug.sethook and debug.gethook
    local old,mask,count
    if dh then old,mask,count=debug.gethook() end
    if S.guard and dh then debug.sethook(function() error('Script instruction limit reached; disable Guard for deliberate long runs.',0) end,'',1000000) end
    local out={pcall(fn,unpack(args))}
    if dh then debug.sethook(old,mask,count) end
    if not out[1] then error(out[2],0) end
    return unpack(out,2)
end
local function stop_run()
    S.running=false; S.user_update=nil; S.user_fullscreen=false
    S.e:tag{'lyprop',id=PROGRAM,visible='0'}
    S.e:tag{'lyprop',id=ROOT,visible='1'}
    S.dirty_draw=true
end
local function start_receive(force)
    if not S.input.valid then start_calibration();return false end
    S.receive=Transfer.new(); S.receive.clock=nil; S.receive.draw_at=0
    S.receive.started=S.e:now();S.receive.last_edge=S.e:now()
    say('PC INPUT: 0 / ? bytes. Calibrated='..tostring(S.input.valid)..'. L cancels. Waiting for Windows.')
    return true
end
local function run()
    local fn,err=loadstring(S.buffer,'@'..S.base..'/'..S.filename)
    assert(fn,err)
    S.running=true; S.output={}; S.user_update=nil
    local api={engine=S.e,slot=S.slot,filename=S.filename,path=S.base..'/'..S.filename}
    api.print=function(...)
        local parts={}; for i=1,select('#',...) do parts[#parts+1]=tostring(select(i,...)) end
        log(table.concat(parts,'\t'))
    end
    api.text=api.print
    api.read=function(name) return W.read(S.base,name) end
    api.write=function(name,data) local ok,why=W.save(S.base,name,data); assert(ok,why); commit(); return true end
    api.openEditor=stop_run
    api.receive=function() stop_run(); return start_receive(false) end
    api.screen=function(color)
        S.e:tag{'lydel',id=PROGRAM}
        S.e:tag{'lyc',id=PROGRAM..'.0',width='1280',height='720',color=color or '0xff1646d8'}
        S.e:tag{'lyprop',id=PROGRAM,left='0',top='0',visible='1',alpha='255'}
        S.e:tag{'lyprop',id=ROOT,visible='0'}
        S.user_fullscreen=true; S.rects={}
        for key in pairs(S.fonts) do if key:sub(1,#PROGRAM)==PROGRAM then S.fonts[key]=nil end end
    end
    api.label=function(id,x,y,size,value) text(tostring(id),x,y,1210,90,size,tostring(value),nil,PROGRAM) end
    api.rect=function(id,x,y,w,h,color)
        local key=PROGRAM..'.r'..tostring(id)
        if not S.rects[key] then S.e:tag{'lyc',id=key,width=tostring(w),height=tostring(h),color=color}; S.rects[key]=true end
        S.e:tag{'lyprop',id=key,left=tostring(x),top=tostring(y),visible='1',alpha='255'}
    end
    S.api=api
    local env=setmetatable({e=S.e,engine=S.e,editor=api,print=api.print},{__index=_G})
    env._G=_G; setfenv(fn,env)
    local returned=guarded(fn,S.e,api)
    if type(returned)=='function' then S.user_update=returned
    elseif type(returned)=='table' and type(returned.update)=='function' then S.user_update=returned.update end
    if not S.receive then say('Running buffer. B returns to editor; files persist after Save + publish.') end
end
local function prompt(kind,initial)
    assert(not S.prompt,'Keyboard already open')
    initial=initial or ''
    if initial:find('%z') then error('Use hex mode for data containing NUL bytes') end
    S.prompt={kind=kind,initial=initial,start=S.cursor}
    if kind=='line' then
        local end_at=S.buffer:find('\n',S.cursor+1,true) or (#S.buffer+1)
        S.prompt.remove=math.min(end_at-1-S.cursor,512)
        initial=S.buffer:sub(S.cursor+1,S.cursor+S.prompt.remove)
        S.prompt.initial=initial
    end
    S.e:tag{'var',name='t.ssedit_input',data=initial}
    local data=W.asb({{'dialog',{title='Seedsow Lua editor / '..kind,message=initial,textfield='t.ssedit_input',textfieldsize='2048'}},
        {'calllua',{['function']='seedsow_editor_keyboard_returned'}},{'wait',{time='0',input='0'}},{'stop',{}}})
    local ok,err=W.put(S.base,'ssedit-keyboard.asb',data); assert(ok,err)
    commit()
    S.e:tag{'jump',file=S.base..'/ssedit-keyboard.asb'}
    say('Console keyboard: finish or cancel there. The character grid remains available.')
end
function seedsow_editor_keyboard_returned()
    if S and S.prompt then S.prompt.ready=true end
end
local function apply_prompt()
    local p=S.prompt; S.prompt=nil
    S.queue={}; S.suppress_until=S.e:now()+250
    local value=S.e:var('t.ssedit_input'); assert(type(value)=='string','Keyboard returned no text')
    if p.kind=='slot' then
        local slot=assert(tonumber(value),'Enter a slot number')
        if dirty_guard('slot:'..slot) then open_slot(slot) end
    elseif p.kind=='filename' then
        if dirty_guard('file:'..value) then read_target(value,true) end
    elseif p.kind=='offset' then
        local n=assert(tonumber(value),'Enter a decimal byte offset')
        assert(n%1==0 and n>=0 and n<=#S.buffer,'Offset must be 0-'..#S.buffer)
        S.cursor=n; say('Cursor at byte '..n)
    elseif p.kind=='deletecount' then
        local n=assert(tonumber(value),'Enter a byte count')
        edit(n,''); say('Deleted '..n..' bytes from buffer; Save file to persist')
    elseif p.kind=='hex' then
        local bytes=W.unhex(value); S.cursor=p.start
        edit(S.patch and math.min(#bytes,#S.buffer-S.cursor) or 0,bytes)
    elseif p.kind=='line' then S.cursor=p.start; edit(p.remove,value)
    else S.cursor=p.start; edit(0,value) end
    S.dirty_draw=true
end
local function insert_key(value)
    if value=='BS' then
        if S.hex_pending~='' then S.hex_pending='' elseif S.cursor>0 then S.cursor=S.cursor-1; edit(1,'') end
    elseif S.hex then
        if value:match('^[%da-fA-F]$') then
            S.hex_pending=S.hex_pending..value
            if #S.hex_pending==2 then
                local bytes=W.unhex(S.hex_pending); S.hex_pending=''
                edit(S.patch and math.min(1,#S.buffer-S.cursor) or 0,bytes)
            end
        else say('Hex mode: enter two hex digits per byte (00 includes NUL).') end
    else edit(0,value) end
    S.dirty_draw=true
end
local function action(name,value)
    if S.prompt then return end
    if S.running then
        if name=='back' or name=='editor' then stop_run() end
        return
    end
    if name=='key' then insert_key(value)
    elseif name=='prevslot' or name=='nextslot' then
        local slot=math.max(4,math.min(S.maxslot,S.slot+(name=='prevslot' and -1 or 1)))
        if dirty_guard(name) then open_slot(slot) end
    elseif name=='slot' then prompt('slot',tostring(S.slot))
    elseif name=='open' then if dirty_guard(name) then open_slot(S.slot) end
    elseif name=='filename' then prompt('filename',S.filename)
    elseif name=='save' then save_file()
    elseif name=='publish' then publish()
    elseif name=='run' then run()
    elseif name=='keyboard' then prompt(S.hex and 'hex' or 'insert','')
    elseif name=='line' then prompt('line','')
    elseif name=='hex' then S.hex=not S.hex; S.hex_pending=''; say(S.hex and 'Hex mode: pairs of digits write bytes.' or 'Text mode')
    elseif name=='patch' then S.patch=not S.patch; say(S.patch and 'Hex PATCH: overwrite bytes at cursor' or 'Hex INSERT: insert bytes at cursor')
    elseif name=='offset' then prompt('offset',tostring(S.cursor))
    elseif name=='left' then S.cursor=math.max(0,S.cursor-1)
    elseif name=='right' then S.cursor=math.min(#S.buffer,S.cursor+1)
    elseif name=='delete' then if S.cursor<#S.buffer then edit(1,'') end
    elseif name=='deletecount' then prompt('deletecount','0')
    elseif name=='back' then insert_key('BS')
    elseif name=='undo' then local prev=table.remove(S.undo); if prev then S.buffer,S.cursor=prev.data,prev.cursor end
    elseif name=='restore' then
        local data,err=W.read(S.base,S.filename..'.bak'); assert(data,err)
        if dirty_guard(name) then S.cursor=0; edit(#S.buffer,data); S.cursor=0; say('Previous .bak in buffer; inspect, then Save file') end
    elseif name=='repair' then say('Repaired '..repair()..' editor files; all three entry slots registered')
    elseif name=='receive' then
        start_receive(false)
    elseif name=='calibrate' then start_calibration()
    elseif name=='inputreport' then
        S.output={S.input:summary(),S.input:timing()};say('Input report: ssedit-input-report.txt / '..S.input:summary())
    elseif name=='guard' then S.guard=not S.guard; say('Instruction guard '..(S.guard and 'ON' or 'OFF')..'; Lua keeps the normal engine and IO APIs')
    elseif name=='title' then
        if dirty_guard(name) then if S.commit_pending then commit() end; S.e:setEventHandler{onEnterFrame=''}; S.e:tag{'reset'}; S.closed=true end
    end
    S.dirty_draw=true
end
local function add_button(label,name,value,x,y,w,h)
    S.buttons[#S.buttons+1]={label=label,name=name,value=value,x=x,y=y,w=w,h=h}
end
local function buttons()
    S.buttons={}
    local toolbar={
        {'Slot -','prevslot'},{'Slot +','nextslot'},{'Choose slot','slot'},{'Open slot','open'},{'Save + publish','publish'},{'RUN buffer','run'},
        {'File / new','filename'},{'Save file','save'},{'Keyboard +','keyboard'},{'Edit line','line'},{'TEXT / HEX','hex'},{'INSERT / PATCH','patch'},
        {'Byte offset','offset'},{'< byte','left'},{'byte >','right'},{'Delete byte','delete'},{'Undo','undo'},{'Restore .bak','restore'},
        {'Receive PC','receive'},{'Repair editors','repair'},{'Guard ON/OFF','guard'},{'Title screen','title'},
        {'Calibrate input','calibrate'},{'Input report','inputreport'}
    }
    for i,b in ipairs(toolbar) do
        local row=math.floor((i-1)/6); local col=(i-1)%6
        add_button(b[1],b[2],nil,20+col*207,72+row*31,201,29)
    end
    local chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'..' '..'!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    for i=1,#chars do
        local c=chars:sub(i,i); local label=c==' ' and 'SPACE' or c
        add_button(label,'key',c,20+((i-1)%14)*89,394+math.floor((i-1)/14)*35,84,32)
    end
    for j,b in ipairs({{'ENTER','\n'},{'TAB','\t'},{'BKSP','BS'}}) do
        local i=#chars+j
        add_button(b[1],'key',b[2],20+((i-1)%14)*89,394+math.floor((i-1)/14)*35,84,32)
    end
end
local function visible(data)
    return (data:gsub('[%z\1-\8\11-\31\127-\255]',function(c) return string.format('<%02X>',c:byte()) end):gsub('\t','  '))
end
local function draw()
    local e=S.e
    text('title',20,8,1240,30,25,'SEEDSOW LUA EDITOR V3 / protected entry slots 1, 2, 3')
    text('info',20,39,1240,30,20,string.format('Slot %d  %s%s  |  %d bytes  |  cursor %d  |  %s %s  |  Guard %s',
        S.slot,S.filename,S.buffer~=S.saved and ' *UNSAVED*' or '',#S.buffer,S.cursor,S.hex and 'HEX' or 'TEXT',S.patch and 'PATCH' or 'INSERT',S.guard and 'ON' or 'OFF'))
    for i,b in ipairs(S.buttons) do
        local label=(i==S.focus and '> ' or '  ')..b.label
        text('b'..i,b.x,b.y,b.w,b.h,i<=22 and 18 or 19,label)
    end
    local start=math.max(0,S.cursor-S.cursor%16-32)
    local preview={}
    if S.running then
        preview[1]='RUNNING / B returns to editor. print(...) appears below.'
        for i=math.max(1,#S.output-5),#S.output do preview[#preview+1]=visible(S.output[i]):sub(1,135) end
    elseif S.hex then
        for row=0,5 do
            local at=start+row*16
            local bytes=S.buffer:sub(at+1,at+16)
            local pairs={}; for i=1,#bytes do pairs[#pairs+1]=string.format('%02X',bytes:byte(i)) end
            preview[#preview+1]=string.format('%06X  %s  | %s',at,table.concat(pairs,' '),(bytes:gsub('[^ -~]','.')))
        end
    else
        local from=math.max(1,S.cursor-250)
        if from>1 then from=(S.buffer:find('\n',from,true) or from)+1 end
        local tail=S.buffer:sub(from,from+2200); local pos=from-1
        for line in (tail..'\n'):gmatch('(.-)\n') do
            if #preview>=6 then break end
            preview[#preview+1]=string.format('%06d %s%s',pos,(S.cursor>=pos and S.cursor<=pos+#line) and '> ' or '  ',visible(line):sub(1,125))
            pos=pos+#line+1
        end
    end
    for i=1,6 do text('p'..i,22,207+(i-1)*29,1238,28,20,preview[i] or '') end
    text('hint',20,642,1240,28,18,'Touch buttons / D-pad selects + A activates / B backspace or stop / L,R move byte / X keyboard / Y run')
    text('status',20,675,1240,35,18,visible(S.status or ''):sub(1,150)..(S.hex_pending~='' and (' | partial hex '..S.hex_pending) or ''))
    e:tag{'flip'}; S.dirty_draw=false
end
local keymap={
    [37]='navleft',[304]='navleft',[39]='navright',[306]='navright',[38]='navup',[305]='navup',[40]='navdown',[307]='navdown',
    [13]='activate',[258]='activate',[27]='back',[257]='back',[260]='left',[261]='right',
    [259]='keyboard',[256]='run'
}
local function enqueue(name,value)
    if #S.queue<32 then S.queue[#S.queue+1]={name,value} end
end
function seedsow_editor_key() end -- Stale V1 callbacks never enqueue input.
function seedsow_editor_event(_engine,name,p)
    if name=='setonpush' then return 1 end
    return 0
end
local function controls()
    local e=S.e
    -- Luaponte exports an event-filter FUNCTION, matching the game's own eventFilter.
    pcall(function() e:setEventFilter(seedsow_editor_event) end)
    local keys={}; for key in pairs(keymap) do keys[key]=true end
    if csv and csv.advkey and csv.advkey.def then for key in pairs(csv.advkey.def) do keys[tonumber(key) or key]=true end end
    for key in pairs(keys) do
        e:tag{'delonpush',key=tostring(key)}
    end
    for role=0,14 do e:tag{'keyconfig',role=tostring(role),keys=''} end
end
local function down(key)
    local ok,value=pcall(function() return S.e:isDown(key) end)
    return ok and (value==true or value==1)
end
local function button_input()
    local groups={}
    for key,name in pairs(keymap) do groups[name]=groups[name] or down(key) end
    if S.input.valid then
        for name,action_name in pairs({A='activate',B='back',X='keyboard',Y='run',L='left',R='right'}) do
            groups[action_name]=S.input:held(name)
        end
    end
    local now=S.e:now()
    for name,held in pairs(groups) do
        local item=S.press[name]
        if not item then item={latched=false,released=now-100}; S.press[name]=item end
        if held then
            if not item.latched then
                item.latched=true
                if not S.suppress_until or now>=S.suppress_until then enqueue(name) end
            end
            item.released=nil
        else
            item.released=item.released or now
            if now-item.released>=50 then item.latched=false end
        end
    end
end
start_calibration=function()
    S.receive=nil;S.running=false;S.user_update=nil;S.input:start();S.calibrate=true
    S.e:tag{'lyprop',id=PROGRAM,visible='0'};S.e:tag{'lyprop',id=ROOT,visible='1'}
    say('CALIBRATION: release all buttons, then Windows sends A B X Y L R in order.')
end
local function calibration_frame()
    S.input:step()
    local c=S.input.cal;local now=S.e:now()
    if not c.report_at or c.report_index~=c.index or now-c.report_at>=15000 then
        local rows={'Seedsow Editor V3 calibration progress','Step '..math.min(c.index,6)..'/6',c.live or '',S.input:timing()}
        for button,counts in pairs(c.results) do
            local values={};for id,row in pairs(counts) do values[#values+1]=id..'='..row.count end
            table.sort(values);rows[#rows+1]=button..' '..table.concat(values,' ')
        end
        W.put(S.base,'ssedit-input-report.txt',table.concat(rows,'\n')..'\n');commit()
        c.report_at=now;c.report_index=c.index
    end
    if not c.draw_at or now-c.draw_at>=150 then
        text('p1',22,207,1238,40,25,'INPUT CALIBRATION / '..(c.done and 'finished' or ('hold physical '..({'A','B','X','Y','L','R'})[c.index]..', then release')))
        text('p2',22,250,1238,60,20,'Windows runs the sequence. Keep every other controller released.')
        text('p3',22,310,1238,80,18,c.live or '')
        text('p4',22,400,1238,60,18,S.input:timing())
        text('p5',22,465,1238,80,18,S.input:summary())
        text('p6',22,550,1238,60,18,'If a step stalls, report the physical button and the isDown/isPush numbers above.')
        text('status',20,675,1240,35,18,'Step '..math.min(c.index,6)..'/6. No program or user save slot is changed.')
        c.draw_at=now
    end
    if c.done then
        local report='Seedsow Editor V3 input calibration\n'..(c.report or '')..'\n'..S.input:timing()..'\n'..(c.error or S.input:summary())..'\n'
        local ok,why=W.put(S.base,'ssedit-input-report.txt',report)
        if not ok then c.error='Cannot write input report: '..tostring(why) end
        if not c.error then local wrote,err=W.put(S.base,'ssedit-controls.txt',c.serialized);if not wrote then c.error=tostring(err) end end
        commit();S.calibrate=false
        if c.error then say('CALIBRATION FAILED: '..c.error..'. Input report saved; choose Calibrate input to retry.')
        else start_receive(true);say('CALIBRATED / PC INPUT: 0 / ? bytes. '..S.input:summary()) end
    end
    S.e:tag{'flip'}
end
local function receive_input()
    local r=S.receive
    S.input:tick()
    local function finish()
        S.receive=nil; S.suppress_until=S.e:now()+300; S.press={}
        for _,name in pairs(keymap) do S.press[name]={latched=true} end
    end
    if S.input:held('L') then finish(); say('PC receive cancelled; buffer unchanged'); return end
    if r.error or r.complete then
        if S.dirty_draw then draw() end
        S.e:tag{'flip'};return
    end
    local function failed(why)
        r.error=tostring(why)
        local report='Seedsow Editor V3 transfer failure\n'..r.error..'\nbytes='..r.count..' edges='..tostring(r.edges or 0)..'\n'..S.input:summary()..'\n'..S.input:timing()..'\n'
        W.put(S.base,'ssedit-transfer-report.txt',report);commit()
        say('PC INPUT ERROR: '..r.error..'. L cancels; error is latched. Report saved.')
        draw()
    end
    local clock=S.input:held('R')
    if r.count>0 and S.e:now()-r.last_edge>10000 then failed('Incomplete packet: input stopped at '..r.count..' / '..tostring(r.expected or '?')..' bytes');return end
    if r.clock==nil then r.clock=clock end
    if r.clock~=clock then
        r.clock=clock
        r.edges=(r.edges or 0)+1;r.last_edge=S.e:now()
        local nibble=(S.input:held('A') and 1 or 0)+(S.input:held('B') and 2 or 0)+(S.input:held('X') and 4 or 0)+(S.input:held('Y') and 8 or 0)
        local ok,why=pcall(Transfer.feed,r,nibble)
        if not ok then failed(why);return end
        if r.complete then
            S.filename=r.name; S.buffer=r.source; S.saved=W.read(S.base,r.name) or ''; S.cursor=0; S.undo={}; S.hex=false
            local mode,name=r.name:match('^([PF]%d%d%d)_(.+)$')
            if mode then
                local saved,err=pcall(function()
                    assert(W.valid(name) and not W.protected(name),'Protected filename')
                    S.filename=name
                    if mode:sub(1,1)=='P' then
                        local slot=tonumber(mode:sub(2));assert(slot>=4 and slot<=S.maxslot,'Protected or invalid user slot')
                        S.slot=slot;publish()
                    else save_file() end
                end)
                if not saved then failed(err);return end
                say(string.format('PC FILE SAVED: %s / %d bytes / %08X%s. L returns.',name,#r.source,r.checksum,mode:sub(1,1)=='P' and (' / SLOT '..S.slot) or ''))
            else say(string.format('PC RECEIVED %d bytes / Adler32 %08X. L returns; then Save + publish or Run.',#r.source,r.checksum)) end
            W.put(S.base,'ssedit-transfer-report.txt',S.status..'\n'..S.input:summary()..'\n'..S.input:timing()..'\n');commit()
            draw()
            return
        end
    end
    if S.e:now()-r.draw_at>=500 then
        text('status',20,675,1240,35,18,'PC INPUT: '..r.count..' / '..tostring(r.expected or '?')..' bytes / edges '..tostring(r.edges or 0)..'. L cancels. '..S.input:timing())
        r.draw_at=S.e:now()
    end
    S.e:tag{'flip'}
end
local function navigate(direction)
    local current=S.buttons[S.focus]; local best,score
    for i,b in ipairs(S.buttons) do
        local dx=(b.x+b.w/2)-(current.x+current.w/2)
        local dy=(b.y+b.h/2)-(current.y+current.h/2)
        local eligible=(direction=='navleft' and dx<0 and math.abs(dy)<20) or (direction=='navright' and dx>0 and math.abs(dy)<20)
            or (direction=='navup' and dy<0) or (direction=='navdown' and dy>0)
        if eligible then
            local s=(direction=='navup' or direction=='navdown') and math.abs(dy)*4+math.abs(dx) or math.abs(dx)
            if not score or s<score then best,score=i,s end
        end
    end
    if best then S.focus=best; S.dirty_draw=true end
end
local function hit(x,y)
    for i,b in ipairs(S.buttons) do
        if x>=b.x and x<b.x+b.w and y>=b.y and y<b.y+b.h then S.focus=i; enqueue(b.name,b.value); return end
    end
end
local function pointer()
    local count=0
    pcall(function() count=tonumber(S.e:getTouchCount()) or 0 end)
    local held=count>0 or down(1)
    if held and not S.touch_down then
        -- The game maps touchscreen input to its mouse coordinates.
        local ok,m=pcall(function() return S.e:getMousePoint() end)
        if ok and type(m)=='table' then hit(tonumber(m.x or m[1]) or -1,tonumber(m.y or m[2]) or -1) end
    end
    S.touch_down=held
end
function seedsow_editor_frame()
    if not S or S.closed then return end
    local ok,err=pcall(function()
        if S.calibrate then calibration_frame();return
        elseif S.receive then receive_input(); if S.receive then return end
        elseif S.prompt then
            if S.prompt.ready then apply_prompt() else return end
        else
            if not S.suppress_until or S.e:now()>=S.suppress_until then pointer() end
            button_input()
            local queue=S.queue; S.queue={}; local seen={}; local now=S.e:now()
            for _,item in ipairs(queue) do
                local name,value=item[1],item[2]; local token=name..':'..tostring(value)
                if not seen[token] and now-(S.last_action[token] or -1000)>=130 then
                    seen[token]=true; S.last_action[token]=now
                    if name:sub(1,3)=='nav' then navigate(name)
                    elseif name=='activate' then local b=S.buttons[S.focus]; action(b.name,b.value)
                    else action(name,value) end
                    if S.prompt or S.closed then break end
                end
            end
        end
        if S.running and S.user_update then
            local good,why=pcall(function() guarded(S.user_update,S.e,S.api) end)
            if not good then stop_run(); log(why); say('Script stopped: '..tostring(why)) end
        end
        if S.commit_pending then commit() end
        if S.user_fullscreen then S.e:tag{'flip'}
        elseif S.dirty_draw and not S.closed then draw() end
    end)
    if not ok then
        S.prompt=nil; S.queue={}; S.receive=nil; stop_run()
        say('ERROR: '..tostring(err)); pcall(draw)
    end
end
function Editor.start(engine,config,source)
    S={e=engine,base=engine:var('s.savepath'),source=source,config=config,
        slot=4,maxslot=math.min(120,(game and tonumber(game.savemax)) or 120),filename='sscode004.lua',buffer='',saved='',cursor=0,
        undo={},queue={},output={},fonts={},focus=1,last_action={},press={},hex=false,hex_pending='',patch=false,guard=true,dirty_draw=true}
    S.input=Input.new(engine,W.read(S.base,'ssedit-controls.txt'))
    for _,id in ipairs({'zzlogn','zzamask','startmask','500','600','2',ROOT}) do engine:tag{'lydel',id=id} end
    engine:tag{'lyc',id=ROOT..'.0',width='1280',height='720',color='0xff14263b'}
    engine:tag{'lyprop',id=ROOT,left='0',top='0',visible='1',alpha='255'}
    for _,tag in ipairs({'autosave','skip','automode'}) do engine:tag{tag,allow='0'} end
    engine:setEventHandler{onEnterFrame='seedsow_editor_frame',onSave='',onLoad='',onClickWaitIn='',onClickWaitOut='',onDebugSkipOut=''}
    if package and type(package.path)=='string' and not package.path:find(S.base..'/?.lua',1,true) then package.path=package.path..';'..S.base..'/?.lua' end
    buttons(); controls()
    local ok,why=pcall(repair)
    if not ok then say('Editor repair/registration: '..tostring(why)) end
    local session=W.read(S.base,'ssedit-session.txt')
    local slot=session and tonumber(session:match('^(%d+)')) or 4
    slot=math.max(4,math.min(S.maxslot,slot or 4))
    local opened,open_error=attempt(function() open_slot(config.run_slot or slot) end)
    if not opened then
        S.slot=4; S.filename=code_name(4); S.buffer=''; S.saved=''; S.cursor=0; S.undo={}
        say('Slot could not open: '..tostring(open_error)..'. File / new can open source or reference files for repair.')
    end
    if config.receive then if S.input.valid then start_receive(true) else start_calibration() end
    elseif config.run_slot and opened then
        local good,err=pcall(run)
        if not good then stop_run(); say('Slot source could not run: '..tostring(err)) end
    elseif opened then say('Ready. Choose slot 4-'..S.maxslot..'; Save + publish makes it loadable after restart. Airplane mode is fine.') end
    if not S.user_fullscreen then draw() end
    return Editor
end
-- Host-side checks exercise these exact operations; not invoked by ordinary UI startup.
function Editor.test_state() return S end
function Editor.test_action(name,value) return action(name,value) end
Editor.storage=W
return Editor
