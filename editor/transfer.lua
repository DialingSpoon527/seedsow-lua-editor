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
