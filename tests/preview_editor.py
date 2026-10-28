"""Render actual recorded UI tags. Requires optional Pillow; not a console capture."""
import argparse
import tempfile
import zipfile
from pathlib import Path

from check import Console


def render(save, output, font,mode='normal'):
    from PIL import Image, ImageDraw, ImageFont
    with zipfile.ZipFile(save) as archive:
        files = {name:archive.read(name) for name in archive.namelist()}
    with tempfile.TemporaryDirectory() as temporary:
        console = Console(files, Path(temporary)/'save')
        console.load(1)
        state = console.state()
        state[b'buffer'] = b'-- Scroll with the labeled toolbar buttons.\nlocal count = 0\n\nreturn function(engine, editor)\n    count = count + 1\n    print(count)\nend\n'
        state[b'cursor'] = 84
        state[b'dirty_draw'] = True
        if mode=='hover':console.point=(40,250)
        elif mode=='selected':console.action('code')
        console.frame()
        background = '#14263b'
        canvas = Image.new('RGB', (1280, 750), background)
        draw = ImageDraw.Draw(canvas)
        for layer in console.shapes.values():
            if layer.get(b'visible',b'1')==b'0':continue
            x,y=int(layer.get(b'left',0)),int(layer.get(b'top',0))
            width,height=int(layer[b'width']),int(layer[b'height'])
            color='#'+layer[b'color'].decode()[-6:]
            draw.rectangle((x,y,x+width-1,y+height-1),fill=color)
        for name, layer in console.layers.items():
            if not layer.get(b'visible', 1) or name not in console.messages:
                continue
            face = ImageFont.truetype(str(font), layer[b'size'])
            tile = Image.new('RGB', (layer[b'width'], layer[b'height']), background)
            ImageDraw.Draw(tile).text((0, 0), console.messages[name].decode('utf-8', errors='replace'),
                                     font=face, fill='white')
            canvas.paste(tile, (layer[b'left'], layer[b'top']))
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0,720,1280,750), fill='#dddddd')
        draw.text((12,724), 'LOCAL LAYOUT PREVIEW / substitute font / not a console capture',
                  font=ImageFont.truetype(str(font),16), fill='black')
        output.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('save', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--font', type=Path, required=True, help='Local TrueType font for the layout preview')
    parser.add_argument('--mode',choices=('normal','hover','selected'),default='normal')
    args = parser.parse_args()
    render(args.save, args.output, args.font,args.mode)
