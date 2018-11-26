import gi
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import json
import subprocess
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

"""
Project details screen for Susereum explorer.
From the explorer screen, user can select any particuar existing project and navigate to this screen to see
the project overview. This screen also provides the additional functionality to view health and history details
"""

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Explorer Details")
        self.set_border_width(5)
        self.set_size_request(600, 300)
        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        # First tab
        self.page1 = Gtk.Box()
        self.page1.set_border_width(10)
        img = Gtk.Image.new_from_file("health.png")
        self.page1.add(img)

        self.notebook.append_page(self.page1, Gtk.Label('Health'))

        # 2nd tab
        self.page2 = Gtk.ScrolledWindow()
        self.page2.set_border_width(10)

        # Required columns for History tab
        self.historical_data = [("Sender ID 1", "Time stamp 1", "Type 1", "Data 1"),
                                ("Sender ID 2", "Time stamp 2", "Type 2", "Data 2")]
        history_list_store = Gtk.ListStore(str, str, str, str)

        # # ListStore (lists that TreeViews can display) and specify data types
        # history_list_store = Gtk.ListStore(str, str)
        for item in self.historical_data:
            history_list_store.append(list(item))

        # TreeView is the item that is displayed
        history_tree_view = Gtk.TreeView(history_list_store)
        # Enumerate to add counter (i) to loop

        for i, col_title in enumerate(["Sender ID", "Time", "Type", "Data"]):
            # Render means draw or display the data (just display as normal text)
            renderer = Gtk.CellRendererText()
            # Create columns (text is column number)
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)
            # Make column sortable and selectable
            column.set_sort_column_id(i)
            # Add columns to TreeView
            history_tree_view.append_column(column)

        self.page2.add(history_tree_view)
        self.notebook.append_page(self.page2, Gtk.Label('History'))

        # 3rd Tab
        self.page3 = Gtk.Box()
        self.page3.set_border_width(10)
        box_users = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.page3.add(box_users)

        # Required columns for History tab
        self.user_data = [("User ID 1", "Suse 1"),
                          ("User ID 2", "Suse 2")]
        user_list_store = Gtk.ListStore(str, str)

        self.listbox_users = Gtk.ListBox()
        self.listbox_users.set_selection_mode(Gtk.SelectionMode.NONE)

        box_users.pack_start(self.listbox_users, True, True, 0)

        self.row = Gtk.ListBoxRow()

        hbox_users = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        self.row.add(hbox_users)

        # # ListStore (lists that TreeViews can display) and specify data types
        # user_list_store = Gtk.ListStore(str, str)
        for item in self.user_data:
            user_list_store.append(list(item))

        # TreeView is the item that is displayed
        user_tree_view = Gtk.TreeView(user_list_store)
        # Enumerate to add counter (i) to loop

        for i, col_title in enumerate(["User ID", "Suse"]):
            # Render means draw or display the data (just display as normal text)
            renderer = Gtk.CellRendererText()
            # Create columns (text is column number)
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)
            # Make column sortable and selectable
            column.set_sort_column_id(i)
            # Add columns to TreeView
            user_tree_view.append_column(column)

        hbox_users.pack_start(user_tree_view, True, True, 0)

        self.listbox_users.add(self.row)

        self.notebook.append_page(self.page3, Gtk.Label('Users'))

        self.connect("delete-event", Gtk.main_quit)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.show_all()


    def get_time_date(self):
        """
          get_time - gets the current date and time stamp
          :returns: time stamp
        """
        return time.strftime("%m-%d-%Y %H:%M")

if __name__ == '__main__':
    window = MainWindow()
    window.connect("delete-event", Gtk.main_quit)
    window.set_position(Gtk.WindowPosition.CENTER)
    window.show_all()
    Gtk.main()
