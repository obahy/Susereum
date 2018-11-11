# read the suse file for this, it is under
# D:\Users\AdEeL\Desktop\Practicum\GitHub-Repo\Susereum\Sawtooth\etc

import gi, time
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Smells")
        self.set_border_width(5)
        self.set_size_request(600, 300)

        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(box_outer)

        # ListStore (lists that TreeViews can display) and specify data types
        projects_list_store = Gtk.ListStore(str, str)

        # Top Section
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        box_outer.pack_start(self.listbox, True, True, 0)

        self.row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.row.add(hbox)
        self.tog_large_class = Gtk.CheckButton("Large class:")
        self.tog_large_class.set_active(True)
        self.tog_large_class.connect("toggled", self.on_tog_large_class)
        hbox.pack_start(self.tog_large_class, True, True, 0)
        self.txt_large_class = Gtk.Entry()
        self.txt_large_class.set_text("0")
        hbox.pack_start(self.txt_large_class, False, True, 0)
        self.listbox.add(self.row)

        self.row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.row.add(hbox)
        self.tog_small_class = Gtk.CheckButton("Small class:")
        self.tog_small_class.set_active(True)
        self.tog_small_class.connect("toggled", self.on_tog_small_class)
        hbox.pack_start(self.tog_small_class, True, True, 0)
        self.txt_small_class = Gtk.Entry()
        self.txt_small_class.set_text("0")
        hbox.pack_start(self.txt_small_class, False, True, 0)
        self.listbox.add(self.row)

        self.row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.row.add(hbox)
        self.tog_large_method = Gtk.CheckButton("Large method:")
        self.tog_large_method.set_active(True)
        self.tog_large_method.connect("toggled", self.on_tog_large_method)
        hbox.pack_start(self.tog_large_method, True, True, 0)
        self.txt_large_method = Gtk.Entry()
        self.txt_large_method.set_text("0")
        hbox.pack_start(self.txt_large_method, False, True, 0)
        self.listbox.add(self.row)

        self.row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.row.add(hbox)
        self.tog_small_method = Gtk.CheckButton("Small method:")
        self.tog_small_method.set_active(True)
        self.tog_small_method.connect("toggled", self.on_tog_small_method)
        hbox.pack_start(self.tog_small_method, True, True, 0)
        self.txt_small_method = Gtk.Entry()
        self.txt_small_method.set_text("0")
        hbox.pack_start(self.txt_small_method, False, True, 0)
        self.listbox.add(self.row)

        self.row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.row.add(hbox)
        self.tog_large_param = Gtk.CheckButton("Large param:")
        self.tog_large_param.set_active(True)
        self.tog_large_param.connect("toggled", self.on_tog_large_param)
        hbox.pack_start(self.tog_large_param, True, True, 0)
        self.txt_large_param = Gtk.Entry()
        self.txt_large_param.set_text("0")
        hbox.pack_start(self.txt_large_param, False, True, 0)
        self.listbox.add(self.row)

        self.row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.row.add(hbox)
        self.tog_god_class = Gtk.CheckButton("God class:")
        self.tog_god_class.set_active(True)
        self.tog_god_class.connect("toggled", self.on_tog_god_class)
        hbox.pack_start(self.tog_god_class, True, True, 0)
        self.txt_god_class = Gtk.Entry()
        self.txt_god_class.set_text("0")
        hbox.pack_start(self.txt_god_class, False, True, 0)
        self.listbox.add(self.row)

        self.row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.row.add(hbox)
        self.tog_inapp_intm = Gtk.CheckButton("Inappropriate Intimacy:")
        self.tog_inapp_intm.set_active(True)
        hbox.pack_start(self.tog_inapp_intm, True, True, 0)
        self.tog_inapp_intm.connect("toggled", self.on_tog_inapp_intm)
        self.txt_inapp_intm = Gtk.Entry()
        self.txt_inapp_intm.set_text("0")
        hbox.pack_start(self.txt_inapp_intm, False, True, 0)
        self.listbox.add(self.row)

        self.row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.row.add(hbox)
        self.tog_ctc_up = Gtk.CheckButton("Comments to code ratio [upper]:")
        self.tog_ctc_up.set_active(True)
        self.tog_ctc_up.connect("toggled", self.on_tog_ctc_up)
        hbox.pack_start(self.tog_ctc_up, True, True, 0)
        self.txt_ctc_up = Gtk.Entry()
        self.txt_ctc_up.set_text("0")
        hbox.pack_start(self.txt_ctc_up, False, True, 0)
        self.listbox.add(self.row)

        self.row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.row.add(hbox)
        self.tog_ctc_lw = Gtk.CheckButton("Comments to code ratio [lower]:")
        self.tog_ctc_lw.set_active(True)
        self.tog_ctc_lw.connect("toggled", self.on_tog_ctc_lw)
        hbox.pack_start(self.tog_ctc_lw, True, True, 0)
        self.txt_ctc_lw = Gtk.Entry()
        self.txt_ctc_lw.set_text("0")
        hbox.pack_start(self.txt_ctc_lw, False, True, 0)
        self.listbox.add(self.row)

        # keep going if more rows are required.

        # Bottom section
        self.listbox_3 = Gtk.ListBox()
        self.listbox_3.set_selection_mode(Gtk.SelectionMode.NONE)
        box_outer.pack_start(self.listbox_3, False, True, 0)

        self.row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.row.add(hbox)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hbox.pack_start(vbox, True, True, 0)
        self.lbl_project = Gtk.Label('Update the code smells values for the project')
        vbox.pack_start(self.lbl_project, True, False, 0)

        self.button = Gtk.Button.new_with_label("Save")
        self.button.connect("clicked", self.open_project)
        hbox.pack_start(self.button, False, True, 0)
        self.listbox_3.add(self.row)

    def on_tog_large_class(self, tog_large_class):
        self.txt_large_class.set_sensitive(tog_large_class.get_active())
        self.txt_large_class.set_text("0")
        #print("Selected")

    def on_tog_small_class (self, tog_small_class):
        self.txt_small_class.set_sensitive(tog_small_class.get_active())
        self.txt_small_class.set_text("0")
        #print("Selected")

    def on_tog_large_method(self, tog_large_method):
        self.txt_large_method.set_sensitive(tog_large_method.get_active())
        self.txt_large_method.set_text("0")
        #print("Selected")

    def on_tog_small_method(self, tog_small_class):
        self.txt_small_method.set_sensitive(tog_small_class.get_active())
        self.txt_small_method.set_text("0")
        #print("Selected")

    def on_tog_large_param(self, tog_large_param):
        self.txt_large_param.set_sensitive(tog_large_param.get_active())
        self.txt_large_param.set_text("0")
        #print("Selected")

    def on_tog_god_class(self, tog_god_class):
        self.txt_god_class.set_sensitive(tog_god_class.get_active())
        self.txt_god_class.set_text("0")
        #print("Selected")

    def on_tog_inapp_intm(self, tog_inapp_intm):
        self.txt_inapp_intm.set_sensitive(tog_inapp_intm.get_active())
        self.txt_inapp_intm.set_text("0")
        #print("Selected")

    def on_tog_ctc_up(self, tog_ctc_up):
        self.txt_ctc_up.set_sensitive(tog_ctc_up.get_active())
        self.txt_ctc_up.set_text("0")
        #print("Selected")

    def on_tog_ctc_lw(self, tog_ctc_lw):
        self.txt_ctc_lw.set_sensitive(tog_ctc_lw.get_active())
        self.txt_ctc_lw.set_text("0")
        # self.button.connect("clicked", self.add_project, projects_list_store)
        # validate_float(txt_ctc_lw)
        #print("Selected")

    def add_project(self, widget, list_store):
        print("Adding project: " + str(self.txt_project.get_text()) + " " + self.get_time_date())
        x = [str(self.txt_large_class.get_text()), self.get_time_date()]
        list_store.append(x)

    def open_project(self, widget):
        from screen_2 import MainWindow
        win = MainWindow()
        #var1.show()

    def get_time_date(self):
        return time.strftime("%m-%d-%Y %H:%M")

    def validate_float(self, widget, entry):
        entry_text = entry.get_text()
        newtext = self.rx.findall(entry_text)
        if len(newtext):
            entry.set_text(newtext[0])
        else:
            entry.set_text("")

window = MainWindow()
window.connect("delete-event", Gtk.main_quit)
window.set_position(Gtk.WindowPosition.CENTER)
window.show_all()
Gtk.main()