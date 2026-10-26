"""Exercise the desktop window without sending any input or using saved credentials."""
import os
import sys
import tempfile
import tkinter as tk
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'pc'))
from app import App


with tempfile.TemporaryDirectory() as temp:
    os.environ['SEEDSOW_SETTINGS'] = str(Path(temp)/'settings.json')
    root = tk.Tk()
    root.attributes('-alpha',0)
    app = App(root)
    root.update()
    assert len(app.tabs.tabs())==4
    assert app.tabs.select()==str(app.install_tab)
    assert app.client is None
    assert b'editor.screen' in app.source()
    app.put_source(bytes(range(256)),'bytes.bin')
    assert app.source()==bytes(range(256))
    assert app.mode.get()=='Raw file'
    assert str(app.text['state'])=='disabled'
    app.quick_proof()
    assert app.raw is None and str(app.text['state'])=='normal'
    for geometry in ('1120x830','940x720'):
        root.geometry(geometry)
        root.update()
        for tab in (app.connect_tab,app.send_tab,app.install_tab,app.control_tab):
            app.tabs.select(tab)
            root.update()
            for child in tab.winfo_children():
                if child.winfo_manager()=='pack':
                    assert child.winfo_ismapped(), (geometry,str(tab),str(child),'hidden')
                    assert child.winfo_y()+child.winfo_height() <= tab.winfo_height()+2, (geometry,str(tab),str(child),'clipped')
    app.close()
print('Desktop smoke check passed: four tabs, binary preservation, fresh proof and visible page layout.')
