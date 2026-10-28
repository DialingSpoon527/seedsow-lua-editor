"""Exercise actual side-editor buttons, cursor positions and rendered code rows."""


def preview(console):
    return [console.messages.get(b'zzzzsseditor.p'+str(i).encode(), b'') for i in range(1,7)]


def check_navigation(c):
    def load(data):
        c.state()[b'saved']=c.state()[b'buffer']
        (c.directory/'navigation-test.lua').write_bytes(data)
        c.prompt('filename','navigation-test.lua')
        c.frame()
        return c.state()

    def action(name):
        c.action(name);c.frame()
        return c.state()

    # Check the emitted text layers, not just the logical hit rectangles.
    buttons=[dict(b.items()) for _,b in c.state()[b'buttons'].items()]
    names={b'lineup',b'linedown',b'scrollup',b'scrolldown',b'pageup',b'pagedown'}
    nav=[b for b in buttons if b[b'name'] in names]
    assert len(nav)==6
    for index,b in c.state()[b'buttons'].items():
        if b[b'name']==b'code':continue
        layer=c.layers[b'zzzzsseditor.b'+str(index).encode()]
        assert layer[b'left']==b[b'x'] and layer[b'top']==b[b'y']
        assert layer[b'width']==b[b'w'] and layer[b'height']==b[b'h']
        assert 0<=b[b'x']<b[b'x']+b[b'w']<=1280
        assert 0<=b[b'y']<b[b'y']+b[b'h']<=650
        if b[b'name'] in names:
            assert layer[b'size']==18 and layer[b'height']>=32
            assert b[b'y']+b[b'h']<=c.layers[b'zzzzsseditor.p1'][b'top']
            assert b[b'label'] in c.messages[b'zzzzsseditor.b'+str(index).encode()]
    for i,a in enumerate(buttons):
        for b in buttons[i+1:]:
            assert (a[b'x']+a[b'w']<=b[b'x'] or b[b'x']+b[b'w']<=a[b'x']
                    or a[b'y']+a[b'h']<=b[b'y'] or b[b'y']+b[b'h']<=a[b'y'])
    assert b'right-hand' not in c.messages[b'zzzzsseditor.hint']

    # Reproduce the original failure: many short lines totaling fewer than 250 bytes.
    lines=[('line%02d'%i).encode() for i in range(1,21)]
    body=b'\n'.join(lines)
    s=load(body)
    cursor=sum(len(line)+1 for line in lines[:12])
    c.prompt('offset',str(cursor));c.frame()
    assert any(row.startswith(b'0013 > [|]line13') for row in preview(c)),preview(c)
    assert s[b'cursor']==cursor and s[b'buffer']==body

    # Vertical moves preserve the original column across short and empty lines.
    body=b'abcdefghi\nx\n\nabcdefghijk\nlast\n'
    s=load(body);c.prompt('offset','8');c.frame()
    for expected in (11,12,21):assert action('linedown')[b'cursor']==expected
    for expected in (12,11,8):assert action('lineup')[b'cursor']==expected
    assert action('lineup')[b'cursor']==8
    c.prompt('offset',str(len(body)));c.frame()
    assert action('linedown')[b'cursor']==len(body)
    assert s[b'buffer']==body

    # Browsing is independent of the insertion cursor, in single lines or pages.
    s=load(b'\n'.join(lines))
    assert action('scrolldown')[b'cursor']==0
    assert preview(c)[0].startswith(b'0002 '),preview(c)
    action('pagedown');assert preview(c)[0].startswith(b'0008 ')
    action('pageup');assert preview(c)[0].startswith(b'0002 ')
    action('scrollup');action('pageup');assert preview(c)[0].startswith(b'0001 ')
    for _ in range(6):action('pagedown')
    assert preview(c)[-1].startswith(b'0020 '),preview(c)
    assert s[b'cursor']==0 and s[b'buffer']==b'\n'.join(lines)
    # A real controller A press activates the new Line down button.
    s[b'focus']=next(i for i,b in s[b'buttons'].items() if b[b'name']==b'linedown')
    c.key(13)
    assert s[b'cursor']==len(lines[0])+1
    assert any(row.startswith(b'0002 > [|]line02') for row in preview(c)),preview(c)

    # Opening a new file, including identical text, resets a manually scrolled view.
    action('pagedown');action('pagedown')
    s=load(b'\n'.join(lines));assert preview(c)[0].startswith(b'0001 > ')

    # Newlines inserted/removed at EOF invalidate line offsets and stay visible.
    c.prompt('offset',str(len(s[b'buffer'])));c.frame()
    original=s[b'buffer']
    c.prompt('keyboard','\nextra\n');c.frame()
    assert any(row.startswith(b'0022 > ') for row in preview(c)),preview(c)
    action('undo');assert s[b'buffer']==original
    assert any(row.startswith(b'0020 > ') for row in preview(c)),preview(c)

    # Horizontal cursor following must not lose a long line's end or short lines.
    s=load(b'A'*180+b'END\nshort\n'+b'B'*180+b'END')
    c.prompt('offset','183');c.frame()
    assert b'END' in preview(c)[0]
    assert action('linedown')[b'cursor']==189
    assert any(row.startswith(b'0002 > short') for row in preview(c)),preview(c)
    assert action('linedown')[b'cursor']==373
    assert b'END' in next(row for row in preview(c) if row.startswith(b'0003 > '))

    # Empty text, boundaries and HEX mode keep their data and byte controls intact.
    s=load(b'')
    for name in ('lineup','linedown','scrollup','scrolldown','pageup','pagedown'):
        action(name);assert s[b'cursor']==0 and s[b'buffer']==b''
    assert preview(c)[0]==b'0001 > [|]' and preview(c)[1:]==[b'']*5,preview(c)
    s=load(b'abcdefgh')
    c.prompt('offset','3');c.frame()
    assert preview(c)[0]==b'0001 > abc[|]defgh',preview(c)
    assert s[b'buffer']==b'abcdefgh'
    s=load(bytes(range(32)))
    action('hex');c.prompt('offset','16');c.frame()
    for name in names:
        action(name.decode());assert s[b'cursor']==16 and s[b'buffer']==bytes(range(32))
    action('right');assert s[b'cursor']==17
    action('hex')

    def tap(x,y):
        c.point=(x,y);c.touch=1;c.frame()
        c.touch=0;c.frame();c.frame()
        return c.state()

    def text_point(row_number,before):
        row=c.state()[b'code_rows'][row_number]
        if row[b'current']:
            cursor=b''.join(b'  ' if byte==9 else ('<%02X>'%byte).encode() if byte<32 or byte>=127 else bytes([byte])
                            for byte in row[b'before'])
            if before.startswith(cursor):before=cursor+b'[|]'+before[len(cursor):]
        return 22+c.measure_width(row[b'prefix']+before)+1,239+(row_number-1)*28+12

    # A full-window focus node sits between navigation and the character grid.
    s=load(b'abcdefghi\nx\n\nabcdefghijk\nlast\n')
    s[b'focus']=next(i for i,b in s[b'buttons'].items() if b[b'name']==b'lineup')
    c.key(307)
    assert s[b'focus']==s[b'code_focus'] and not s[b'code_selected']
    assert c.shapes[b'zzzzsseditor.codefocus'][b'color']==b'0xffc4d9ee'
    c.key(13)
    assert s[b'code_selected'] is True
    assert c.shapes[b'zzzzsseditor.codefocus'][b'color']==b'0xff000000'
    c.prompt('offset','8');c.frame()
    for expected in (11,12,21):c.key(307);assert s[b'cursor']==expected
    for expected in (12,11,8):c.key(305);assert s[b'cursor']==expected
    c.key(304);assert s[b'cursor']==7
    c.key(306);assert s[b'cursor']==8
    before=s[b'buffer'];focus=s[b'focus']
    c.key(27)
    assert not s[b'code_selected'] and s[b'buffer']==before and s[b'cursor']==8
    assert s[b'focus']==focus
    assert c.shapes[b'zzzzsseditor.codefocus'][b'color']==b'0xffc4d9ee'
    c.key(307);assert s[b'focus']!=s[b'code_focus'] and s[b'cursor']==8

    # Hovering shows the line without selecting or moving the cursor.
    s=load(b'WiWi\nsecond\n\nlast')
    s[b'focus']=1;c.point=(45,250);c.frame()
    assert not s[b'code_selected'] and s[b'cursor']==0
    assert c.shapes[b'zzzzsseditor.codefocus'][b'color']==b'0xffc4d9ee'
    c.point=(-1,-1);c.frame()
    assert c.shapes[b'zzzzsseditor.codefocus'][b'visible']==b'0'
    # Proportional text widths place taps by glyphs, not average character width.
    tap(*text_point(2,b'sec'));assert s[b'cursor']==8 and s[b'code_selected']
    tap(*text_point(1,b'WiW'));assert s[b'cursor']==3
    row=s[b'code_rows'][1]
    x=22+c.measure_width(row[b'prefix']+row[b'before'])+4
    tap(x,251);assert s[b'cursor']==3 # Inside [|] still means the same insertion point.
    tap(1250,251);assert s[b'cursor']==4
    tap(1250,239+2*28+12);assert s[b'cursor']==12 # Empty line.
    tap(1000,239+5*28+12);assert s[b'cursor']==len(s[b'buffer']) # Blank row below EOF.

    # Measured hit testing also maps tabs and escaped bytes to original offsets.
    s=load(b'\tA\x00B\n')
    tap(*text_point(1,b'  A'));assert s[b'cursor']==2
    tap(*text_point(1,b'  A<00>'));assert s[b'cursor']==3

    # Both manual vertical scrolling and horizontal following retain file offsets.
    s=load(b'\n'.join(lines));action('pagedown')
    tap(*text_point(3,b'li'))
    assert s[b'cursor']==sum(len(line)+1 for line in lines[:8])+2
    s=load(b'A'*180+b'END\nshort')
    c.prompt('offset','183');c.frame()
    row=s[b'code_rows'][1];offset=row[b'offset']
    assert offset>0
    tap(*text_point(1,b'AA'));assert s[b'cursor']==offset+2

    # Held arrows repeat only in cursor mode, and X-style text entry preserves it.
    s=load(b'abcdefghijklmno');c.action('code');c.frame()
    c.held={306}
    for _ in range(5):c.frame()
    c.held=set();c.frame();c.frame()
    assert s[b'cursor']>1 and s[b'code_selected']
    c.prompt('keyboard','!');c.frame();assert s[b'code_selected']
    before=s[b'buffer'];c.key(27);assert s[b'buffer']==before and not s[b'code_selected']

    # The same selection works on hex bytes; Up/Down step one 16-byte row.
    s=load(bytes(range(64)));action('hex')
    c.action('code');c.frame();c.key(307);assert s[b'cursor']==16
    c.key(306);assert s[b'cursor']==17
    c.key(305);assert s[b'cursor']==1
    row=s[b'code_rows'][1]
    x=22+c.measure_width(row[b'prefix']+b'00 ')+1
    tap(x,251);assert s[b'cursor']==1
    before=s[b'buffer'];c.key(27);assert s[b'buffer']==before and not s[b'code_selected']
    action('hex');c.point=(-1,-1)
    # The Switch dialog itself accepts 32; longer edits require manual insertions.
    s=load(b'');c.action('keyboard');c.reply('x'*40);c.frame()
    assert s[b'buffer']==b'x'*32
    c.prompt('keyboard','y'*80);c.frame()
    assert s[b'buffer']==b'x'*32+b'y'*80
    c.state()[b'saved']=c.state()[b'buffer']
    print('Navigation, measured touch placement, code focus, D-pad cursor mode and B exit passed.')
