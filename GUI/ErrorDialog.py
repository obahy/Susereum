import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def ErrorDialog(self, message):
    d = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, message)
    d.run()
    d.destroy()
