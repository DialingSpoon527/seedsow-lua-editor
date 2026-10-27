"""Guided Windows desktop app. Python 3.10+ with Tk; no pip dependencies."""
import json
import os
import queue
import secrets
import subprocess
import sys
import threading
import time
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from client import BridgeClient, load_settings, save_settings, settings_path, upload_request

ROOT = Path(__file__).resolve().parent.parent
VERSION = '0.1.2'


class App:
    def __init__(self,root):
        self.root = root
        self.events = queue.Queue()
        self.closed = False
        self.polling = False
        self.local_busy = False
        self.transfer_active = False
        self.client = None
        self.raw = None
        self.last_result = None
        root.title('Seedsow Lua Editor — PC Companion')
        root.geometry('1120x830')
        root.minsize(940,720)
        root.protocol('WM_DELETE_WINDOW',self.close)
        style = ttk.Style(root)
        if 'vista' in style.theme_names():
            style.theme_use('vista')
        style.configure('Title.TLabel',font=('Segoe UI',21,'bold'))
        style.configure('Section.TLabel',font=('Segoe UI',12,'bold'))
        style.configure('Hint.TLabel',foreground='#495b6d')
        style.configure('TButton',padding=(10,6))
        frame = ttk.Frame(root,padding=20)
        frame.pack(fill='both',expand=True)
        ttk.Label(frame,text='Seedsow Lua Editor',style='Title.TLabel').pack(anchor='w')
        ttk.Label(frame,text='Install once. Write Lua on your console. Optional uploads from Windows.',style='Hint.TLabel').pack(anchor='w',pady=(3,12))
        self.connection_status = tk.StringVar(value='The console editor works on its own. A Pi connection is optional for PC uploads.')
        ttk.Label(frame,textvariable=self.connection_status,wraplength=1000).pack(anchor='w',pady=(0,12))
        self.tabs = ttk.Notebook(frame)
        self.tabs.pack(fill='both',expand=True)
        self.connect_tab = ttk.Frame(self.tabs,padding=18)
        self.send_tab = ttk.Frame(self.tabs,padding=18)
        self.install_tab = ttk.Frame(self.tabs,padding=18)
        self.control_tab = ttk.Frame(self.tabs,padding=18)
        for tab,title in [(self.install_tab,'Install save & updates'),(self.connect_tab,'Optional: connect Pi'),
                          (self.send_tab,'Optional: send files'),(self.control_tab,'Controller')]:
            self.tabs.add(tab,text=title)
        self.status = tk.StringVar(value='For installation, download the prepared save and follow the guide. Builders below are optional.')
        ttk.Label(frame,textvariable=self.status,wraplength=1020,padding=(0,12)).pack(fill='x')
        self.progress = ttk.Progressbar(frame,mode='determinate')
        self.progress.pack(fill='x')
        self.connect_page()
        self.send_page()
        self.install_page()
        self.control_page()
        self.quick_proof()
        # Tk themes and fallback fonts need different vertical space on each host.
        root.update_idletasks()
        root.minsize(940,max(720,root.winfo_reqheight()))
        try:
            config = load_settings()
            if config:
                self.show_config(config)
                self.client = BridgeClient(config)
                self.tabs.select(self.send_tab)
        except (OSError,ValueError) as error:
            self.status.set('Saved settings could not load: '+str(error))
        root.after(100,self.drain)
        root.after(500,self.poll)

    def label(self,parent,text):
        ttk.Label(parent,text=text,style='Section.TLabel').pack(anchor='w',pady=(0,8))

    def hint(self,parent,text):
        ttk.Label(parent,text=text,style='Hint.TLabel',wraplength=960,justify='left').pack(anchor='w',pady=(0,12))

    def connect_page(self):
        page = self.connect_tab
        self.label(page,'Connect to your Raspberry Pi')
        self.hint(page,'Install the bridge on the Pi once, then import its private connection file. '
                  'Windows and the Pi need the same LAN. Keep console airplane mode ON with controller Bluetooth enabled and Wi-Fi OFF, including during pairing.')
        row = ttk.Frame(page)
        row.pack(fill='x',pady=(0,12))
        ttk.Button(row,text='Open setup guide',command=lambda:self.open_doc('02-pi-setup.md')).pack(side='left')
        ttk.Button(row,text='Import connection file…',command=self.import_config).pack(side='left',padx=8)
        self.host = tk.StringVar(value='raspberrypi.local')
        self.port = tk.StringVar(value='39391')
        self.token = tk.StringVar()
        fields = ttk.Frame(page)
        fields.pack(fill='x')
        for index,(title,var,width,show) in enumerate([('Pi address',self.host,40,''),('Port',self.port,10,''),('Connection token',self.token,65,'•')]):
            ttk.Label(fields,text=title).grid(row=index,column=0,sticky='w',padx=(0,12),pady=5)
            ttk.Entry(fields,textvariable=var,width=width,show=show).grid(row=index,column=1,sticky='w',pady=5)
        ttk.Button(page,text='Save & test connection',command=self.connect).pack(anchor='w',pady=12)
        ttk.Separator(page).pack(fill='x',pady=8)
        self.label(page,'Pair as Player 1, then calibrate once')
        self.hint(page,'1. On the console open Controllers → Change Grip/Order. Click Pair controller, then make the Pi Player 1.\n'
                  '2. Return to Seedsow. Open PC INPUT / CALIBRATE in slot 2. The first time it asks you to hold physical A.\n'
                  '3. Confirm that screen below, then click Calibrate. Keep all other controls released for about 18 seconds.')
        ttk.Button(page,text='Pair controller',command=self.pair).pack(anchor='w',pady=(0,10))
        self.calibration_ready = tk.BooleanVar()
        ttk.Checkbutton(page,text='Console is on INPUT CALIBRATION, waiting for physical A',variable=self.calibration_ready).pack(anchor='w')
        ttk.Button(page,text='Calibrate controller',command=self.calibrate).pack(anchor='w',pady=10)
        self.hint(page,'Success is PC INPUT: 0 / ? bytes on the console. The editor may leave an old “hold R” heading above it. '
                  'Once calibrated, loading slot 2 arms the receiver directly; do not recalibrate for every file.')

    def send_page(self):
        page = self.send_tab
        self.label(page,'Choose a file or write Lua here')
        bar = ttk.Frame(page)
        bar.pack(fill='x',pady=(0,8))
        for title,fn in [('Open file…',self.open_file),('New proof',self.quick_proof),('Blue animation',self.demo),('Save on PC…',self.save_file)]:
            ttk.Button(bar,text=title,command=fn).pack(side='left',padx=(0,6))
        self.filename = tk.StringVar(value='pc-proof.lua')
        self.mode = tk.StringVar(value='Lua launch slot')
        self.slot = tk.StringVar(value='20')
        self.speed = tk.StringVar(value='Normal')
        row = ttk.Frame(page)
        row.pack(fill='x',pady=(0,10))
        ttk.Label(row,text='Save filename').pack(side='left')
        ttk.Entry(row,textvariable=self.filename,width=26).pack(side='left',padx=6)
        ttk.Combobox(row,textvariable=self.mode,values=['Lua launch slot','Raw file'],state='readonly',width=16).pack(side='left',padx=6)
        ttk.Label(row,text='Slot').pack(side='left')
        self.slot_field = ttk.Entry(row,textvariable=self.slot,width=5)
        self.slot_field.pack(side='left',padx=6)
        ttk.Label(row,text='Speed').pack(side='left')
        ttk.Combobox(row,textvariable=self.speed,values=['Normal','Slow','Fast'],state='readonly',width=8).pack(side='left',padx=6)
        self.mode.trace_add('write',lambda *_:self.slot_field.configure(state='normal' if self.mode.get()=='Lua launch slot' else 'disabled'))
        self.text = tk.Text(page,wrap='none',font=('Consolas',11),undo=True,height=12)
        self.text.pack(fill='both',expand=True)
        self.file_info = tk.StringVar()
        ttk.Label(page,textvariable=self.file_info,wraplength=960,style='Hint.TLabel').pack(anchor='w',pady=8)
        self.receiver_ready = tk.BooleanVar()
        ttk.Checkbutton(page,text='Console slot 2 is armed and shows PC INPUT: 0 / ? bytes',variable=self.receiver_ready).pack(anchor='w')
        self.send_button = ttk.Button(page,text='Send & save',command=self.send)
        self.send_button.pack(side='left',pady=10)
        ttk.Button(page,text='Stop sending',command=lambda:self.call('/stop',{},'Sending stopped. Hold L on the console to leave its receiver.')).pack(side='left',padx=8)
        ttk.Button(page,text='Upload guide',command=lambda:self.open_doc('03-send-files.md')).pack(side='right')

    def install_page(self):
        page = self.install_tab
        self.label(page,'Start here: install the already-built save')
        self.hint(page,'Download the prepared save, restore it with JKSV on a homebrew-capable Switch 1, then use Nintendo save transfer to Switch 2. '
                  'No backup-building step or Pi is needed. See the guide for account and online-transfer requirements.')
        row = ttk.Frame(page)
        row.pack(fill='x',pady=(0,8))
        ttk.Button(row,text='Download prepared save',command=lambda:webbrowser.open(
            'https://github.com/DialingSpoon527/seedsow-lua-editor/releases/latest/download/Seedsow-Lua-Editor-Save.zip')).pack(side='left')
        ttk.Button(row,text='Step-by-step installation',command=lambda:self.open_doc('01-console-install.md')).pack(side='left',padx=8)
        self.label(page,'Optional: build a custom compatible save')
        self.hint(page,'For developers or custom saves: choose your own compatible backup. Existing editor backups retain user programs. '
                  'Input stays unchanged; output is a new private ZIP in build/.')
        self.base_zip = tk.StringVar()
        row = ttk.Frame(page)
        row.pack(fill='x')
        ttk.Entry(row,textvariable=self.base_zip,width=75).pack(side='left',fill='x',expand=True)
        ttk.Button(row,text='Choose backup ZIP…',command=self.choose_backup).pack(side='left',padx=8)
        self.allow_install = tk.BooleanVar()
        ttk.Checkbutton(page,text='First installation: I have a backup and allow replacing slots 1–3',variable=self.allow_install).pack(anchor='w',pady=12)
        ttk.Button(page,text='Build installation ZIP',command=self.build_installer).pack(anchor='w')
        ttk.Separator(page).pack(fill='x',pady=10)
        self.label(page,'Build an editor update for another slot')
        self.hint(page,'This creates a small Lua upload from your installed editor base and the source in this repo. '
                  'Upload it to a fresh slot; keep original slots 1–3 and your last working version. '
                  'The new version still relies on the base loader. Hardware testing of this side editor is pending.')
        self.update_slot = tk.StringVar(value='30')
        row = ttk.Frame(page)
        row.pack(fill='x')
        ttk.Label(row,text='New editor slot').pack(side='left')
        ttk.Entry(row,textvariable=self.update_slot,width=6).pack(side='left',padx=10)
        ttk.Button(row,text='Build update & open for sending',command=self.build_update).pack(side='left')
        ttk.Button(page,text='Update & recovery guide',command=lambda:self.open_doc('04-updates-recovery.md')).pack(anchor='w',pady=(6,4))
        self.build_info = tk.StringVar(value='Generated save ZIPs and updates are private build outputs, excluded from Git and source releases.')
        ttk.Label(page,textvariable=self.build_info,wraplength=860,style='Hint.TLabel').pack(anchor='w',pady=(4,0))

    def control_page(self):
        page = self.control_tab
        self.label(page,'Manual controller')
        self.hint(page,'Use these buttons to navigate while the Pi is Player 1. '
                  'Transmission temporarily disables manual input. Confirm the console screen before calibration or sending.')
        grid = ttk.Frame(page)
        grid.pack(anchor='w',pady=15)
        for i,(label,button) in enumerate([('←','DPAD_LEFT'),('↑','DPAD_UP'),('↓','DPAD_DOWN'),('→','DPAD_RIGHT'),
                                           ('A','A'),('B','B'),('X','X'),('Y','Y'),('L','L'),('R','R')]):
            ttk.Button(grid,text=label,width=7,command=lambda b=button:self.call('/tap',{'button':b},'Sent '+b.replace('DPAD_',''))).grid(row=i//5,column=i%5,padx=5,pady=5)
        ttk.Button(page,text='Hold L / leave receiver',command=lambda:self.call('/tap',{'button':'L','down':1.0,'up':.3},'Sent L. Check the console; re-arm slot 2 before another upload.')).pack(anchor='w',pady=8)
        ttk.Button(page,text='Troubleshooting',command=lambda:self.open_doc('05-troubleshooting.md')).pack(anchor='w',pady=8)
        self.hint(page,'After an upload, hold L, then load the destination slot from the game’s load menu. '
                  'Stop sending stops the Pi; it does not close the console receiver.')

    def work(self,fn,success=None):
        def worker():
            try:
                result = fn()
                if success:
                    self.events.put(lambda r=result:success(r))
            except Exception as error:
                self.events.put(lambda message=str(error):self.show_error(message))
        threading.Thread(target=worker,daemon=True).start()

    def drain(self):
        if self.closed:
            return
        for _ in range(100):
            try:
                fn = self.events.get_nowait()
            except queue.Empty:
                break
            fn()
        self.root.after(100,self.drain)

    def show_error(self,message):
        self.local_busy = False
        self.status.set(message)
        messagebox.showerror('Seedsow',message,parent=self.root)

    def show_config(self,config):
        self.host.set(config.get('host','raspberrypi.local'))
        self.port.set(str(config.get('port',39391)))
        self.token.set(config.get('token',''))

    def import_config(self):
        path = filedialog.askopenfilename(title='Private Pi connection file',filetypes=[('JSON','*.json')])
        if not path:
            return
        try:
            config = json.loads(Path(path).read_text(encoding='utf-8-sig'))
            BridgeClient(config)
            self.show_config(config)
            self.connect()
        except (ValueError,OSError) as error:
            self.show_error(str(error))

    def connect(self):
        try:
            config = save_settings({'host':self.host.get(),'port':self.port.get(),'token':self.token.get()})
            self.client = BridgeClient(config)
            self.call('/status',None,'Connection works. Pair the Pi as Player 1 if needed.')
        except (ValueError,OSError) as error:
            self.show_error(str(error))

    def call(self,path,data,message):
        if not self.client:
            return self.show_error('Import or save your Pi connection settings first.')
        client = self.client
        self.work(lambda:client.request(path,data),lambda _:self.status.set(message))

    def pair(self):
        self.calibration_ready.set(False)
        self.receiver_ready.set(False)
        self.call('/pair',{'backend':'controller','reset':True},'Pairing started. Register the Pi as Player 1 in Change Grip/Order.')

    def calibrate(self):
        if not self.calibration_ready.get():
            return self.show_error('Open the console calibration screen waiting for A, then tick the confirmation above.')
        self.calibration_ready.set(False)
        self.call('/calibrate',{},'Calibration inputs started. Leave other controls released; check the console after 18 seconds.')

    def source(self):
        return self.raw if self.raw is not None else self.text.get('1.0','end-1c').encode('utf-8')

    def put_source(self,source,name):
        self.text.configure(state='normal')
        self.text.delete('1.0','end')
        self.filename.set(name)
        self.raw = None
        try:
            value = source.decode('utf-8')
            if '\0' in value:
                raise ValueError('binary')
            self.text.insert('1.0',value)
            self.mode.set('Lua launch slot')
            self.file_info.set(f'{len(source):,} bytes loaded. Lua launch slot saves and publishes; Raw file stores exact bytes.')
        except (UnicodeError,ValueError):
            self.raw = source
            self.text.insert('1.0',f'BINARY PREVIEW — {len(source):,} bytes\n\n'+source[:2048].hex(' '))
            self.text.configure(state='disabled')
            self.mode.set('Raw file')
            self.file_info.set('Binary preview is read-only; sending and saving use the exact original bytes.')

    def open_file(self):
        path = filedialog.askopenfilename()
        if path:
            try:
                if Path(path).stat().st_size > 1048576:
                    raise ValueError('File exceeds the 1 MiB receiver limit.')
                self.put_source(Path(path).read_bytes(),Path(path).name)
            except (ValueError,OSError) as error:
                self.show_error(str(error))

    def save_file(self):
        path = filedialog.asksaveasfilename(initialfile=self.filename.get())
        if path:
            try:
                Path(path).write_bytes(self.source())
                self.status.set('Saved local file: '+path)
            except OSError as error:
                self.show_error(str(error))

    def quick_proof(self):
        token = 'PC-'+secrets.token_hex(3).upper()
        source = ("editor.screen('0xff1646d8')\nreturn function(e,p)\n p.label(1,30,30,36,'"+token+
                  " '..e:now())\n p.rect(1,30+e:now()%1100,300,80,20,'0xffffffff')\nend\n").encode()
        self.put_source(source,'pc-proof.lua')
        self.file_info.set('Proof token: '+token+'. After PC FILE SAVED, load your chosen slot and look for this token and a moving bar.')

    def demo(self):
        token = 'PC-'+secrets.token_hex(4).upper()
        self.put_source((ROOT/'examples/blue.lua').read_bytes().replace(b'@@TOKEN@@',token.encode()),'pc-blue.lua')

    def send(self):
        if not self.client:
            return self.show_error('Set up the Pi connection on the Optional: connect Pi tab.')
        if not self.receiver_ready.get():
            return self.show_error('Arm console slot 2 and confirm its zero count before sending.')
        try:
            if self.raw is not None and self.mode.get() != 'Raw file':
                raise ValueError('Binary files use Raw file mode.')
            slot = int(self.slot.get()) if self.mode.get()=='Lua launch slot' else None
            body,eta = upload_request(self.filename.get().strip(),self.source(),slot,self.speed.get())
            if self.transfer_active:
                raise ValueError('A transfer is already running.')
            self.receiver_ready.set(False)
            self.status.set(f'Starting upload; estimate {eta/60:.1f} minutes. Keep console controls released.')
            self.call('/send',body,'Pi is sending. Wait for PC FILE SAVED on the console, then hold L and load the destination slot.')
        except (ValueError,KeyError) as error:
            self.show_error(str(error))

    def choose_backup(self):
        path = filedialog.askopenfilename(title='Your current compatible backup',filetypes=[('Backup ZIP','*.zip')])
        if path:
            self.base_zip.set(path)

    def run_builder(self,script,args,success):
        if self.local_busy:
            return self.show_error('A package build is already running.')
        if not self.base_zip.get():
            return self.show_error('Choose your own backup ZIP above first.')
        self.local_busy = True
        self.build_info.set('Building…')
        command = [sys.executable,str(ROOT/'editor'/script),'--base',self.base_zip.get()]+args
        def build():
            result = subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',
                                    errors='replace',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            if result.returncode:
                raise ValueError(result.stderr.strip()[-2000:] or 'Build failed.')
            return json.loads(result.stdout)
        def complete(info):
            self.local_busy = False
            success(info)
        self.work(build,complete)

    def build_installer(self):
        def done(info):
            self.build_info.set('Installation ZIP ready: '+info['save_zip'])
            self.status.set('Build complete. Follow the console installation guide to restore your private ZIP.')
            messagebox.showinfo('Installation ZIP ready',info['save_zip']+'\n\nInput backup unchanged. See the installation guide for restore steps.',parent=self.root)
        self.run_builder('build.py',['--replace-slots'] if self.allow_install.get() else [],done)

    def build_update(self):
        try:
            slot = int(self.update_slot.get())
            if not 4 <= slot <= 120:
                raise ValueError('Choose an unused slot from 4 to 120.')
        except ValueError as error:
            return self.show_error(str(error))
        def done(info):
            path = Path(info['lua_file'])
            self.put_source(path.read_bytes(),path.name)
            self.slot.set(str(info['slot']))
            self.receiver_ready.set(False)
            self.build_info.set('Update ready: '+str(path))
            self.tabs.select(self.send_tab)
            self.status.set('Update built. Arm slot 2, send it, then load slot '+str(info['slot'])+'. Keep original slots 1–3.')
        self.run_builder('build_side_editor.py',['--slot',str(slot)],done)

    def poll(self):
        if self.closed:
            return
        if self.client and not self.polling:
            self.polling = True
            client = self.client
            def fetch():
                try:
                    value = client.request('/status')
                    self.events.put(lambda:self.update_bridge(value) if client is self.client else None)
                except Exception as error:
                    self.events.put(lambda message=str(error):self.connection_status.set(message) if client is self.client else None)
                finally:
                    self.events.put(lambda:setattr(self,'polling',False))
            threading.Thread(target=fetch,daemon=True).start()
        self.root.after(2000,self.poll)

    def update_bridge(self,value):
        ctrl = value.get('controller',{})
        state = str(ctrl.get('state','unknown'))
        player = ctrl.get('player_number')
        self.connection_status.set('Pi reachable · Controller: '+state+(f' · Player {player}' if player else ''))
        job = value.get('transfer')
        self.transfer_active = bool(job)
        self.send_button.configure(state='disabled' if job else 'normal')
        if job:
            elapsed = max(0,time.time()-job['started'])
            estimate = max(1,job.get('estimated_seconds',1))
            self.progress['value'] = min(99,100*elapsed/estimate)
            self.status.set(f"{job.get('state','sending').capitalize()}: {job.get('bytes',0):,} bytes · "
                            f"{elapsed:.0f}s elapsed · about {max(0,estimate-elapsed):.0f}s remaining (estimate)")
        else:
            last = value.get('last')
            if last and last != self.last_result:
                self.last_result = last
                if last.get('state')=='failed':
                    self.status.set('Pi transmission failed: '+last.get('error','Unknown error'))
                    self.progress['value'] = 0
                else:
                    self.status.set(str(last.get('state',''))+'. '+str(last.get('note','')))
                    self.progress['value'] = 100 if last.get('state')=='input sent' else 0

    def open_doc(self,name):
        path = ROOT/'docs'/name
        if sys.platform=='win32':
            os.startfile(path)
        else:
            import webbrowser
            webbrowser.open(path.as_uri())

    def close(self):
        if self.transfer_active and not messagebox.askyesno('Transfer is still running',
                'Closing the app leaves the Pi sending. Close anyway? Use Stop sending to cancel first.',parent=self.root):
            return
        self.closed = True
        self.root.destroy()


if __name__ == '__main__':
    app_root = tk.Tk()
    App(app_root)
    app_root.mainloop()
