-- Text navigation shared by the main editor and updates. Positions are bytes.
local Navigation={}
Navigation.__index=Navigation
local ROWS,COLUMNS=6,88
local function clamp(n,low,high) return math.max(low,math.min(high,n)) end
function Navigation.new()
    return setmetatable({top=1,left=0,follow=true,starts={1}},Navigation)
end
function Navigation:reset()
    self.buffer=nil;self.cursor=nil;self.preferred=nil
    self.top=1;self.left=0;self.follow=true
end
function Navigation:sync(buffer)
    if self.buffer==buffer then return end
    self.buffer=buffer;self.starts={1}
    local at=1
    while true do
        local found=buffer:find('\n',at,true)
        if not found then break end
        self.starts[#self.starts+1]=found+1;at=found+1
    end
    self.cursor=nil;self.preferred=nil;self.follow=true
    self.top=clamp(self.top,1,math.max(1,#self.starts-ROWS+1))
end
function Navigation:locate(cursor)
    local low,high=1,#self.starts
    while low<high do
        local mid=math.floor((low+high+1)/2)
        if self.starts[mid]-1<=cursor then low=mid else high=mid-1 end
    end
    return low,cursor-(self.starts[low]-1)
end
function Navigation:length(line)
    return (self.starts[line+1] and self.starts[line+1]-2 or #self.buffer)-(self.starts[line]-1)
end
function Navigation:reveal(line,column)
    if line<self.top then self.top=line
    elseif line>=self.top+ROWS then self.top=line-ROWS+1 end
    self.top=clamp(self.top,1,math.max(1,#self.starts-ROWS+1))
    if column<COLUMNS then self.left=0
    elseif column<self.left then self.left=column
    elseif column>=self.left+COLUMNS then self.left=column-COLUMNS+1 end
end
function Navigation:move(buffer,cursor,delta)
    self:sync(buffer)
    local line,column=self:locate(cursor)
    if self.cursor~=cursor then self.preferred=nil end
    local preferred=self.preferred or column
    local target=clamp(line+delta,1,#self.starts)
    -- At the first/last line, leave the insertion position unchanged.
    if target~=line then cursor=self.starts[target]-1+math.min(preferred,self:length(target)) end
    self.cursor=cursor;self.preferred=preferred;self.follow=true
    local actual,column_now=self:locate(cursor)
    self:reveal(actual,column_now)
    return cursor,actual,#self.starts,column_now
end
function Navigation:scroll(buffer,cursor,delta)
    self:sync(buffer)
    self.cursor=cursor;self.preferred=nil;self.follow=false
    self.top=clamp(self.top+delta,1,math.max(1,#self.starts-ROWS+1))
    return self.top,math.min(#self.starts,self.top+ROWS-1),#self.starts
end
function Navigation:preview(buffer,cursor)
    self:sync(buffer)
    if self.cursor~=cursor then self.preferred=nil;self.follow=true end
    self.cursor=cursor
    local line,column=self:locate(cursor)
    if self.follow then self:reveal(line,column) end
    local rows={}
    for number=self.top,math.min(#self.starts,self.top+ROWS-1) do
        local first=self.starts[number]
        local last=first-1+self:length(number)
        local text=buffer:sub(math.min(last+1,first+self.left),math.min(last,first+self.left+COLUMNS-1))
        local split=clamp(column-self.left,0,#text)
        rows[#rows+1]={line=number,current=number==line,text=text,offset=math.min(last,first+self.left-1),
            before=text:sub(1,split),after=text:sub(split+1)}
    end
    return rows
end
return Navigation
