"""Temporary BlueZ pairing agent restricted to Nintendo Switch named devices."""
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus=dbus.SystemBus()

class Rejected(dbus.DBusException):_dbus_error_name='org.bluez.Error.Rejected'

class Agent(dbus.service.Object):
    def allow(self,path):
        obj=bus.get_object('org.bluez',path)
        properties=dbus.Interface(obj,'org.freedesktop.DBus.Properties')
        values=properties.GetAll('org.bluez.Device1')
        names=[str(values.get(k,'')).casefold() for k in ('Name','Alias')]
        if not any(name in ('nintendo switch','nintendo switch 2') for name in names):
            print('Rejected unrelated Bluetooth pairing request',flush=True);raise Rejected('Not the requested console')
        properties.Set('org.bluez.Device1','Trusted',dbus.Boolean(True))
        print('Accepted Nintendo console pairing authorization',flush=True)

    @dbus.service.method('org.bluez.Agent1',in_signature='',out_signature='')
    def Release(self):pass
    @dbus.service.method('org.bluez.Agent1',in_signature='o',out_signature='')
    def RequestAuthorization(self,path):self.allow(path)
    @dbus.service.method('org.bluez.Agent1',in_signature='ou',out_signature='')
    def RequestConfirmation(self,path,passkey):self.allow(path)
    @dbus.service.method('org.bluez.Agent1',in_signature='os',out_signature='')
    def AuthorizeService(self,path,uuid):
        if str(uuid) not in ('00001124-0000-1000-8000-00805f9b34fb','00001000-0000-1000-8000-00805f9b34fb'):
            raise Rejected('Only controller HID services are allowed')
        self.allow(path)
    @dbus.service.method('org.bluez.Agent1',in_signature='',out_signature='')
    def Cancel(self):pass

if __name__=='__main__':
    agent=Agent(bus,'/seedsow/input/agent')
    manager=dbus.Interface(bus.get_object('org.bluez','/org/bluez'),'org.bluez.AgentManager1')
    manager.RegisterAgent('/seedsow/input/agent','NoInputNoOutput')
    manager.RequestDefaultAgent('/seedsow/input/agent')
    loop=GLib.MainLoop();GLib.timeout_add_seconds(600,lambda:(loop.quit(),False)[1])
    print('Nintendo-only pairing agent ready (10 minute window)',flush=True)
    try:loop.run()
    finally:manager.UnregisterAgent('/seedsow/input/agent')
