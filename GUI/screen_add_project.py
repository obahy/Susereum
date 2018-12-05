import gi, time
import subprocess
import sys
import os
import screen_smells
import requests
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from ErrorDialog import ErrorDialog
"""
Add project screen for Susereum.
Uses the provided URL for the project in order to add the project
After the project is added, code smells screen appears for the user to enter initial smells values
After savign smells, user can select an existing project from the list and navigate to the prodect details screen.
"""

class MainWindow(Gtk.Window):
    def __init__(self, user_id_,num_id_):
        Gtk.Window.__init__(self, title="Susereum Projects")
        self.user_id = user_id_
        self.num_id = num_id_
        self.projects=[]
        self.read_projects()

        # Testing new changes... [adding additional 2 columns]
        #self.projects=[("Project 1", "Project Name 1", "1024", "11-11-2018"),
        #                   ("Project 2", "Project Name 2", "2048", "12-12-2018")]

        self.set_border_width(5)
        self.set_size_request(600, 300)

        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(box_outer)

        # ListStore (lists that TreeViews can display) and specify data types

        # Testing new changes... [adding additional 2 columns]
        #projects_list_store = Gtk.ListStore(str, str)
        projects_list_store = Gtk.ListStore(str, str, str, str)  # New Change#

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

        # Testing new changes... [adding additional 2 columns]
        #for i, col_title in enumerate(["Project", "Date"]):
        for i, col_title in enumerate(["ID", "Project Name", "Suse", "Date"]):
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

        # Encapsulate the Projects Tree View in a Scrolled Window and pack into box_outer.
        scrolled_window = Gtk.ScrolledWindow()
        box_outer.pack_start(scrolled_window, True, True, 0)
        scrolled_window.add(projects_tree_view)

        # Bottom section
        self.listbox_3 = Gtk.ListBox()
        self.listbox_3.set_selection_mode(Gtk.SelectionMode.NONE)
        box_outer.pack_start(self.listbox_3, False, True, 0)

        self.row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.row.add(hbox)
        #vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.lbl_suse = Gtk.Label(self.user_id+" Suse:")
        hbox.pack_start(self.lbl_suse, True, True, 0)

        suse_value = "0000"
        self.lbl_suse_value = Gtk.Label()
        self.lbl_suse_value.set_markup("<b>"+  ("{0:.2f}".format(self.total_suse)) +"</b>")
        hbox.pack_start(self.lbl_suse_value, True, True, 0)

        self.lbl_project = Gtk.Label('Select project to delete/view')
        hbox.pack_start(self.lbl_project, True, True, 0)
        self.btn_delete = Gtk.Button.new_with_label("Delete")
        self.btn_delete.connect("clicked", self.delete_project)
        hbox.pack_start(self.btn_delete, False, True, 0)
        self.button = Gtk.Button.new_with_label("Details")
        self.button.connect("clicked", self.open_project)
        hbox.pack_start(self.button, False, True, 0)
        self.listbox_3.add(self.row)

        self.connect("delete-event", Gtk.main_quit)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.show_all()
        #Gtk.main()

    def read_projects(self):
        """
          read_projects - checks if there are any existing projects added to Susereum and adds them to the list view.
          format: [("Project 1", "Project Name 1", "1024", "11-11-2018"),
        #                   ("Project 2", "Project Name 2", "2048", "12-12-2018")]
        """
        self.total_suse = 0.0
        for prj in os.listdir((os.environ['HOME'])+'/.sawtooth_projects/'):
            if prj == '.' or prj == '..' or not prj.startswith('.'):
                continue
            #TODO query suse
            suse = 0.0
            try:
                ports = open((os.environ['HOME'])+'/.sawtooth_projects/'+prj+ '/etc/.ports').read()
                api = ports.split('\n')[2].strip()
                command = 'sawtooth transaction list --url http://127.0.0.1:'+api+' | grep '+str(self.num_id)+' | grep b\\\'suse, | head -n 1 | awk "{print $5}"'
                out = os.popen(command).read()
                print("OUT,OUT,OUT,OUT,",out)
                if ',' in out:
                    suse = out.split(',')[2]
            except Exception as e:
                print('Getting SUSE err:', e)

            self.total_suse = float(self.total_suse) + float(suse)
            self.projects.append((prj[1:].split('_')[1], prj[1:].split('_')[0], ("{0:.2f}".format(float(suse))), self.get_time_date()))

            #TODO check if proccess is running for this prj

    def is_valid_url(self, url):
        if 'http://' not in url or '/connect/tmp' not in url:
            ErrorDialog(self, "Error!\nInvalid Project URL!")
            return False
        try:
            r = requests.get(url)
            if r.status_code != 200:
                ErrorDialog(self, "Error!\nUnable to connect to project! Invalid URL!")
                return False
        except requests.exceptions.ConnectionError:
            ErrorDialog(self, "Error!\nUnable to connect to Susereum server!")
            return False
        if '[about]' not in r.text:
            ErrorDialog(self, "Error!\nInvalid file at " + url)
            return False
        return True

    def add_project(self, widget, list_store):
        """
          add_projects - Takes the url from the project field and runs the new chain client script.
                         checks and opens the smells screen for the newly added project
          :param widget: list_store
        """

        #call newchain script
        url = str(self.txt_project.get_text())
        if not self.is_valid_url(url):
            return
        #repo_path = sys.argv[0]
        repo_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        #repo_path = '\\'.join(repo_path.split('\\')[0:-2])
        print('GOING TO RUN:',['../ServerSideScripts/new_chain_client.sh',url,repo_path])
        subprocess.Popen(['../ServerSideScripts/new_chain_client.sh',url,repo_path])
        time.sleep(5)
        self.list_store = list_store
        #win = screen_smells.MainWindow(url, self)
        #win.show()
        #ask for smell #TODO check if smells exist
        r = requests.get(url)
        data = r.text.split('\n')
        prj_name = data[3]
        prj_id = data[4]
        api = data[2]
        print(['./check_smell.sh', str(api)])
        subprocess.Popen(['./check_smell.sh', str(api)])#TODO I am not correct CHECKKKKKKKKKKK XD
        time.sleep(3)
        if os.path.isfile('smells_exist.txt'):
            print('SMEELL EXSISTS................................................... ')
            print('SMEELL EXSISTS................................................... ')
            x = [prj_id,prj_name,"0",self.get_time_date()]#TODO query health
            print('SMEELL EXSISTS: ',x)
            print('SMEELL EXSISTS: ', x)
            print('SMEELL EXSISTS: ', x)
            print('SMEELL EXSISTS: ', x)
            print('SMEELL EXSISTS: ', x)
            print('SMEELL EXSISTS: ', x)
            print('SMEELL EXSISTS: ', x)
            self.list_store.append(x)
        else:
            win = screen_smells.MainWindow(url, self)
            win.show()

    def delete_project(self, widget):
        """
          delete_projects - Takes the url from the project field and runs the new chain client script.
                         checks and opens the smells screen for the newly added project
          :param widget: list_store
        """
        print("Deleting project")
        if not self.selected:
            return
        import shutil
        shutil.rmtree(os.environ['HOME']+'/.sawtooth_projects/'+self.selected)
        #TODO remove label


    def open_project(self, widget):
        """
            open_project - opens the selected project details on the new screen..
            :param widget: widget
        """
        from screen_details import MainWindow
        win = MainWindow(os.environ['HOME']+'/.sawtooth_projects/'+self.selected) # ENABLE THIS LINE TOO AND DELETE NEXT LINE!!!


    def get_time_date(self):
        """
          get_time_date - to get the current date and time
          :returns: timestamp
        """
        return time.strftime("%m-%d-%Y %H:%M")

    def item_selected(self, selection):
        """
          item_selected - fetch the selected item details from the list view.
          :param: selected row
        """
        model, row = selection.get_selected()
        if row is not None:
            print("\nSelection- " + "ID: " + str(model[row][0]) + " Name: " + str(model[row][1]) + "\n")
            self.selected = "."+str(model[row][1])+"_"+str(model[row][0])


if __name__ == '__main__':
    window = MainWindow()
    window.connect("delete-event", Gtk.main_quit)
    window.set_position(Gtk.WindowPosition.CENTER)
    window.show_all()
    Gtk.main()
