import gi, time
import os
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import re
from itertools import dropwhile
import requests
import subprocess
import json

"""
Sawtooth Explorer screen for Susereum.
This screen is used to list all the projects and enables the user to select any particular project and see related details
User can also search the projects from this screen
"""

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Susereum Explorer")

        #TODO: Martin you can read data that you want to display on the list and add it to projects below.
        self.projects=[]#[("Project 1", "Project Name 1", "Health value 1", "11-11-2018"),("Project 2", "Project Name 2", "Health value 2", "12-12-2018")]
        self.read_projects()
        self.set_border_width(5)
        self.set_size_request(600, 300)

        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(box_outer)

        # ListStore (lists that TreeViews can display) and specify data types
        self.projects_list_store = Gtk.ListStore(str, str, str, str)  # New Change#
        self.filter = self.projects_list_store.filter_new()
        self.list_store = self.projects_list_store

        # # removed search functionality
        # # Top Section
        # self.listbox = Gtk.ListBox()
        # self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        # box_outer.pack_start(self.listbox, False, True, 0)
        #
        # self.row = Gtk.ListBoxRow()
        # hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        # self.row.add(hbox)
        # vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # hbox.pack_start(vbox, True, True, 0)
        # self.txt_project = Gtk.Entry()
        # self.txt_project.set_text("Project")
        # vbox.pack_start(self.txt_project, True, True, 0)
        # self.btn_search = Gtk.Button.new_with_label("Search")
        # self.btn_search.connect("clicked", self.search_project, self.projects_list_store)
        #
        # hbox.pack_start(self.btn_search, False, True, 0)
        # self.listbox.add(self.row)
        # # keep going if more rows are required.

        #middle section
        self.listbox_2 = Gtk.ListBox()
        box_outer.pack_start(self.listbox_2, True, True, 0)

        self.row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        self.row.add(hbox)


        for item in self.projects:
            self.projects_list_store.append(list(item))

        """
        for row in projects_list_store:
            print(row[:])  # Print all data
        """

        # TreeView is the item that is displayed
        projects_tree_view = Gtk.TreeView(self.projects_list_store)
        # Enumerate to add counter (i) to loop

        # Testing new changes... [adding additional 2 columns]
        #for i, col_title in enumerate(["Project", "Date"]):
        for i, col_title in enumerate(["ID", "Project Name", "Health", "Date"]):
            # Render means draw or display the data (just display as normal text)
            renderer = Gtk.CellRendererText()
            renderer.props.wrap_width = 250
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
        self.btn_details = Gtk.Button.new_with_label("Show Details")
        self.btn_details.connect("clicked", self.show_details)

        hbox.pack_start(self.btn_details, False, True, 0)
        self.listbox_3.add(self.row)

        self.connect("delete-event", Gtk.main_quit)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.show_all()

    def findnth(self, haystack, needle, n):
        parts= haystack.split(needle, n+1)
        if len(parts) <= n+1:
            return -1
        return len(haystack)-len(parts[-1])-len(needle)

    def add_project(self, url):
        """
          add_projects - Takes the url from the project field and runs the new chain client script.
                         checks and opens the smells screen for the newly added project
          :param widget: list_store
        """
        #new chain equivalent
        repo_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        print(url)
        r = requests.get(url)
        data = r.text.split('\n')
        prj_name = str(data[3].encode('utf-8'))[2:-1]
        prj_id = str(data[4].encode('utf-8'))[2:-1]
        api = str(data[2].encode('utf-8'))[2:-1]

        home = str((os.environ['HOME']+'/.sawtooth_projects/').encode('utf-8'))[2:-1]
        #print(home, prj_name, prj_id)
        #print(type(home), type(prj_name), type(prj_id))
        etc_dir = home+"."+prj_name+"_"+prj_id+"/etc/"

        print(['python3', '../Sawtooth/bin/health.py', 'list', '--type', 'health', '--url',
               'http://129.108.7.2:' + str(api)])
        results = subprocess.check_output(['python3', '../Sawtooth/bin/health.py', 'list', '--type', 'health', '--url',
                                           'http://129.108.7.2:' + str(api)])
        if not results:
            health = "50"
        else:
            results = results.decode('utf-8').replace("'", "\"").replace('": b"', '": "').strip()
            dictionary = json.loads(results)
            for value in dictionary.values():
                dataz = value.split(',')
                print(dataz)
                health = dataz[2]
                if '-2' in health:
                    health = "-"
                else:
                    break

        try:
            if not os.path.exists(etc_dir):
                os.makedirs(etc_dir)
        except:
            print("ERROR: Couldn't make " + etc_dir)


        """
        try:
            os.mkdir(home)
        except:
            print('couldnt make ' + home)
            pass
        try:

            os.mkdir(home+"."+prj_name+"_"+prj_id)
        except:
            print('couldnt make home2')
            pass
        try:
            os.mkdir(home+"."+prj_name+"_"+prj_id+"/etc")
        except:
            print('couldnt make home3')
            pass
        """

        ports = open(etc_dir+'.ports','w+')
        suse = open(etc_dir+'.suse','w+')
        #repo = open(os.listdir((os.environ['HOME'])+'/.sawtooth_projects/.'+prj_name+"_"+prj_id+"/etc/")+'.repo','w')
        ports.write(data[0]+'\n')
        ports.write(data[1]+'\n')
        ports.write(data[2]+'\n')
        ports.close()
        suse.write(r.text[self.findnth(r.text,'\n',3):])
        suse.close()
        x = [prj_id,prj_name,health,self.get_time_date()]#TODO query suse
        self.projects.append(x)
       

    def read_projects(self):
        """
          read_projects - checks if there are any existing projects added to Susereum and adds them to the list view.
        """
        r = requests.get('http://129.108.7.2/project_list.php')#check if there are project
        urls = r.text.split('\n')
        #print(r.text)
        for url in urls:
            #print(url)
            if "http" in url:
                self.add_project(url.strip())
        '''for prj in os.listdir((os.environ['HOME'])+'/.sawtooth_projects/'):
            if prj == '.' or prj == '..' or not prj.startswith('.'):
                continue
            list_item = (prj[1:],self.get_time_date())
            if list_item in 
            self.projects.append()'''

    # removed search functionality.
    # def search_project(self, widget, list_store):
    #     """
    #       search_project -
    #       :param widget: list_store
    #     """

    def show_details(self, widget):
        """
            show_details - opens the selected project details on the new screen..
            :param widget: widget
        """
        from screen_explorer_details import MainWindow
        print("Opening details at " + str(self.selected_api_port) + " REST API port")
        win = MainWindow(self.selected_api_port)

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
            print("\nSelection-" + str(model[row][0]) + ", " +str(model[row][1]) + ", " +str(model[row][2]) + ", " + str(model[row][3]))
            self.selected = str(model[row][0])

            # Get REST API port from ~/.sawtooth_projects/<prj_name>_<prj_id>/etc/.ports
            home = str((os.environ['HOME']+'/.sawtooth_projects/').encode("ascii"))[2:-1]
            prj_id = str(model[row][0])
            prj_name = str(model[row][1])
            #print(home, prj_name, prj_id)
            #print(type(home), type(prj_name), type(prj_id))
            ports_dir = home+"."+prj_name+"_"+prj_id+"/etc/"+'.ports'
            ports_file = open(ports_dir,'r')
            ports_string = str(ports_file.read().encode('ascii'))[2:-1]
            #print(type(ports_string))
            #print(ports_string)
            #print(ports_string.split('\\n'))
            self.selected_api_port = int(ports_string.split('\\n')[2])           # REST API is the third line
            ports_file.close()

    # def visible_cb(self, model, iter, data=None):
    #     '''
    #     :param model:
    #     :param iter:
    #     :param data:
    #     :return:
    #     '''
    #     search_query = self.entry.get_text().lower()
    #     active_category = self.catcombo.get_active()
    #     search_in_all_columns = active_category == 0
    #
    #     if search_query == "":
    #         return True
    #
    #     if search_in_all_columns:
    #         for col in range(1,self.treeview.get_n_columns()):
    #             value = model.get_value(iter, col).lower()
    #             if value.startswith(search_query):
    #                 return True
    #
    #         return False
    #
    #     value = model.get_value(iter, active_category).lower()
    #     return True if value.startswith(search_query) else False

window = MainWindow()
window.connect("delete-event", Gtk.main_quit)
window.set_position(Gtk.WindowPosition.CENTER)
window.show_all()
Gtk.main()
