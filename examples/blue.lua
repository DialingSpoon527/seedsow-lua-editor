local p=editor
p.screen('0xff1646d8')
p.label('title',40,32,48,'PC PROGRAM / BLUE SCREEN')
p.label('proof',40,110,28,'@@TOKEN@@')
p.label('help',40,620,24,'B: return to editor. Save + publish keeps this program.')
local start=engine:now()
local last=-1
return function(e,api)
 local t=e:now()-start
 for i=1,12 do
  local x=50+(i*89+t*.08)%1150
  local y=260+math.sin(t/700+i)*100
  api.rect(i,math.floor(x),math.floor(y),18,18,'0xffffffff')
 end
 api.rect('bar',40+math.floor(t%6000*1100/6000),510,100,14,'0xffffcc33')
 if math.floor(t/100)~=last then
  last=math.floor(t/100)
  api.label('clock',40,180,28,string.format('Elapsed %.1f seconds / engine tick %d',t/1000,e:now()))
 end
end
