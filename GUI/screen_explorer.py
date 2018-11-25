import gi, time
import os
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

"""
Sawtooth Explorer screen for Susereum.
This screen is used to list all the projects and enables the user to select any particular project and see related details
User can also search the projects from this screen
"""

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Susereum Explorer")

        #TODO: Martin you can read data that you want to display on the list and add it to projects below.
        self.projects=[("Project 1", "Project Name 1", "Health value 1", "11-11-2018"),
                           ("Project 2", "Project Name 2", "Health value 2", "12-12-2018")]

        self.set_border_width(5)
        self.set_size_request(600, 300)

        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(box_outer)

        # ListStore (lists that TreeViews can display) and specify data types
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
        self.btn_search = Gtk.Button.new_with_label("Search")
        self.btn_search.connect("clicked", self.search_project, projects_list_store)

        hbox.pack_start(self.btn_search, False, True, 0)
        self.listbox.add(self.row)
        # keep going if more rows are required.

        #middle section
        self.listbox_2 = Gtk.ListBox()
        box_outer.pack_start(self.listbox_2, True, True, 0)

        self.row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        self.row.add(hbox)


        for item in self.projects:
            projects_list_store.append(list(item))

        for row in projects_list_store:
            print(row[:])  # Print all data

        # TreeView is the item that is displayed
        projects_tree_view = Gtk.TreeView(projects_list_store)
        # Enumerate to add counter (i) to loop

        # Testing new changes... [adding additional 2 columns]
        #for i, col_title in enumerate(["Project", "Date"]):
        for i, col_title in enumerate(["ID", "Project Name", "Health", "Date"]):
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
        self.btn_details = Gtk.Button.new_with_label("Show Details")
        self.btn_details.connect("clicked", self.show_details)

        hbox.pack_start(self.btn_details, False, True, 0)
        self.listbox_3.add(self.row)

        self.connect("delete-event", Gtk.main_quit)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.show_all()

    def read_projects(self):
        """
          read_projects - checks if there are any existing projects added to Susereum and adds them to the list view.
        """
        for prj in os.listdir((os.environ['HOME'])+'/.sawtooth_projects/'):
            if prj == '.' or prj == '..' or not prj.startswith('.'):
                continue
            self.projects.append((prj[1:],self.get_time_date()))


    def search_project(self, widget, list_store):
        """
          search_project -
          :param widget: list_store
        """

    def show_details(self, widget):
        """
            show_details - opens the selected project details on the new screen..
            :param widget: widget
        """
        from screen_explorer_details import MainWindow
        win = MainWindow()
        #TODO: Martin add your functionality here...


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


window = MainWindow()
window.connect("delete-event", Gtk.main_quit)
window.set_position(Gtk.WindowPosition.CENTER)
window.show_all()
Gtk.main()
