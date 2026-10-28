-- Learn physical controller buttons from held-state APIs, including game aliases.
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
