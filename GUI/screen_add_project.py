import gi, time
import subprocess
import sys
import os
import screen_smells
import requests
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
'''
 = [("Project 1", "11-11-2018 09:38"),
            ("Project 2", "11-10-2018 09:38"),
            ("Project 3", "11-09-2018 09:38"),
            ("Project 4", "11-08-2018 09:38"),
            ("Project 5", "11-07-2018 09:38")]
'''
class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Susereum Projects")
        self.projects=[]
        self.read_projects()

        self.set_border_width(5)
        self.set_size_request(600, 300)

        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(box_outer)

        # ListStore (lists that TreeViews can display) and specify data types
        projects_list_store = Gtk.ListStore(str, str)

        # Top Section
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        box_outer.pack_start(self.listbox, False, True, 0)

        self.row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.row.add(hbox)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hbox.pack_start(vbox, True, True, 0)
        self.txt_project = Gtk.Entry()
        self.txt_project.set_text("Project")
        vbox.pack_start(self.txt_project, True, True, 0)
        self.button = Gtk.Button.new_with_label("Add Project")
        self.button.connect("clicked", self.add_project, projects_list_store)

        hbox.pack_start(self.button, False, True, 0)
        self.listbox.add(self.row)
        # keep going if more rows are required.

        #middle section
        self.listbox_2 = Gtk.ListBox()
        box_outer.pack_start(self.listbox_2, True, True, 0)

        self.row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        self.row.add(hbox)

        # # ListStore (lists that TreeViews can display) and specify data types
        # projects_list_store = Gtk.ListStore(str, str)
        for item in self.projects:
            projects_list_store.append(list(item))

        # x = ["hi", "test"]
        # projects_list_store.append(x)

        for row in projects_list_store:
            print(row[:])  # Print all data

        # TreeView is the item that is displayed
        projects_tree_view = Gtk.TreeView(projects_list_store)
        # Enumerate to add counter (i) to loop
        for i, col_title in enumerate(["Project", "Date"]):
            # Render means draw or display the data (just display as normal text)
            renderer = Gtk.CellRendererText()
            # Create columns (text is column number)
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)
            # Make column sortable and selectable
            column.set_sort_column_id(i)
            # Add columns to TreeView
            projects_tree_view.append_column(column)

        # Handle selection
        selected_row = projects_tree_view.get_selection()
        selected_row.connect("changed", self.item_selected)

        hbox.pack_start(projects_tree_view, True, True, 0)

        self.listbox_2.add(self.row)

        # Bottom section
        self.listbox_3 = Gtk.ListBox()
        self.listbox_3.set_selection_mode(Gtk.SelectionMode.NONE)
        box_outer.pack_start(self.listbox_3, False, True, 0)

        self.row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.row.add(hbox)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hbox.pack_start(vbox, True, True, 0)
        self.lbl_project = Gtk.Label('Select a project to view details')

        vbox.pack_start(self.lbl_project, True, True, 0)
        self.button = Gtk.Button.new_with_label("Show Details")
        self.button.connect("clicked", self.open_project)

        hbox.pack_start(self.button, False, True, 0)
        self.listbox_3.add(self.row)

        self.connect("delete-event", Gtk.main_quit)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.show_all()
        #Gtk.main()

    def read_projects(self):
        for prj in os.listdir((os.environ['HOME'])+'/.sawtooth_projects/'):
            if prj == '.' or prj == '..':
                continue
            self.projects.append((prj[1:],self.get_time_date()))


    def add_project(self, widget, list_store):
        #call newchain script
        url = str(self.txt_project.get_text())
        #repo_path = sys.argv[0]
        repo_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        #repo_path = '\\'.join(repo_path.split('\\')[0:-2])
        print('GOING TO RUN:',['../ServerSideScripts/new_chain_client.sh',url,repo_path])
        subprocess.Popen(['../ServerSideScripts/new_chain_client.sh',url,repo_path])
        #ask for smell #TODO check if smells exist
        subprocess.Popen(['./check_smell.sh', url])
        time.sleep(2)
        if os.path.exists('smells_exist.txt'):
            os.remove('smells_exist.txt')
            r = requests.get(self.url)
            data = r.text.split('\n')
            self.pbrj_name = data[3]
            x = [self.prj_name, self.get_time_date()]
            list_store.append(x)
        else:
            self.list_store = list_store
            win = screen_smells.MainWindow(url, self)
            win.show()
        '''
        print("Adding project: " + str(self.txt_project.get_text()) + " " + self.get_time_date())
        x = [prj_name, self.get_time_date()]
        list_store.append(x)
        from screen_smells import MainWindow
        win = MainWindow()
        '''

    def open_project(self, widget):
        from screen_details import MainWindow
        win = MainWindow()
        #win.show()
        #var1.show()

    def get_time_date(self):
        return time.strftime("%m-%d-%Y %H:%M")

    def item_selected(self, selection):
        model, row = selection.get_selected()
        if row is not None:
            print("\nSelection- " + "Project: " + str(model[row][0]) + " Date: " + str(model[row][1]) + "\n")


if __name__ == '__main__':
    window = MainWindow()
    window.connect("delete-event", Gtk.main_quit)
    window.set_position(Gtk.WindowPosition.CENTER)
    window.show_all()
    Gtk.main()
