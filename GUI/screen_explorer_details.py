import gi
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import json
import subprocess
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import requests     # Have to manually send requests to each blockchain REST API bc Sawtooth doesn't support 32-bit architecture
import base64

"""
Project details screen for Susereum explorer.
From the explorer screen, user can select any particuar existing project and navigate to this screen to see
the project overview. This screen also provides the additional functionality to view health and history details
"""

class MainWindow(Gtk.Window):

    def __init__(self, api_port):
        self.username_mappings = {}

        Gtk.Window.__init__(self, title="Explorer Details")
        self.set_border_width(5)
        self.set_size_request(800, 1000)
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
        self.historical_data = []

        transactions = self.blockchain_requests(api_port, "/transactions")
        suse_transactions = []      # To be used later to calculate user/suse tab

        try:
            for transaction in transactions['data']:
                #sender_id = transaction['header']['batcher_public_key']
                payload = base64.b64decode(transaction['payload'])     # Returns base64 encoded comma-delimited payload
                payload_list = payload.split(',')
                #print("Payload: " + str(payload_list))
                #user_github_id = payload_list[1]
                #user_github_username = self.github_user_id_to_username(user_github_id)
                #print(user_github_username)
                #print("Payload: " + str(payload_list))
                transaction_type = payload_list[0]      # Transactions type is always the first item

                sender_id = "Anonymous"
                if(transaction_type in ["commit", "health", "suse"]):
                    user_github_id = payload_list[1]
                    sender_id = self.github_user_id_to_username(user_github_id)

                # Filter out transactions
                if(transaction_type not in ["code_smell", "commit", "health", "proposal", "suse", "vote"]):
                    continue

                # Prepare labels for data, different transaction types have different labels
                if(transaction_type == "suse"):
                    suse_transactions.append(transaction)

                timestamp = payload_list[len(payload_list) - 1]     # Timestamp is always the last item

                data = ""       # Data is everything in between
                i = 1
                while(i < len(payload_list) - 1):
                    data += payload_list[i] + "\n"
                    i += 1

                self.historical_data.append((sender_id, timestamp, transaction_type, data))     # Add a tuple to the list to show in table
        except:
            print("Problem trying to parse the history transactions")

        #self.historical_data = [("Sender ID 1", "Time stamp 1", "Type 1", "Data 1"),
        #                       ("Sender ID 2", "Time stamp 2", "Type 2", "Data 2")]
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
            renderer.props.wrap_width = 250
            # Create columns (text is column number)
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)
            # Make column sortable and selectable
            column.set_sort_column_id(i)
            # Add columns to TreeView
            history_tree_view.append_column(column)

        self.page2.add(history_tree_view)
        self.notebook.append_page(self.page2, Gtk.Label('History'))

        # 3rd Tab
        self.page3 = Gtk.ScrolledWindow()
        self.page3.set_border_width(10)

        # Required columns for History tab
        self.user_data = []     # List of users and their suse values to be rendered
        suse_sums = {}          # dictionary to sum up suse values for each user

        # Loop through all transactions of type suse, parse user id and suse awarded
        # Sum up the suse values for each user and render them in a table
        for suse_transaction in suse_transactions:
            payload = base64.b64decode(suse_transaction['payload'])     # Returns base64 encoded comma-delimited payload
            payload_list = payload.split(',')
            user_github_id = payload_list[1]
            user_github_username = self.github_user_id_to_username(user_github_id)
            suse_awarded = float(payload_list[2])      # TODO: CHRISTIAN Add in the index of the suse value in the payload

            # Add suse to user in dict or create a new key-value in the dict
            if user_github_username in suse_sums:
                suse_sums[user_github_username] += suse_awarded
            else:
                suse_sums[user_github_username] = suse_awarded

        # Add user and sum values to self.user_data to be rendered
        for user_github_username, suse_sum in suse_sums.items():
            suse_sum_formatted = str(format(suse_sum, '.2f'))
            self.user_data.append((user_github_username, suse_sum_formatted))     # Adds tuple to the user_data for rendering

        # Adding them dynamically now
        #self.user_data = [("User ID 1", "Suse 1"),
        #                  ("User ID 2", "Suse 2")]
        user_list_store = Gtk.ListStore(str, str)

        self.listbox_users = Gtk.ListBox()
        self.listbox_users.set_selection_mode(Gtk.SelectionMode.NONE)

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
            renderer.props.wrap_width = 250
            # Create columns (text is column number)
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)
            # Make column sortable and selectable
            column.set_sort_column_id(i)
            # Add columns to TreeView
            user_tree_view.append_column(column)

        self.page3.add(user_tree_view)
        self.notebook.append_page(self.page3, Gtk.Label('Users'))

        self.connect("delete-event", Gtk.main_quit)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.show_all()

    def github_user_id_to_username(self, id):
        username = ""
        if id in self.username_mappings:
            username = self.username_mappins[id]
            return username

        try:
            url = "https://api.github.com/user/" + id
            r = requests.get(url)
            username = r.json()['login'].encode('ascii')     # unicode to ascii
            return username
        except:
            print("Problem trying to convert GitHub user id to username. You only have 60 requests/hour.")
        return str(id)

    def blockchain_requests(self, api_port, endpoint):
        """
        Makes GET request to blockchain. Hard coded server IP.

        Args:
            api_port: The port of the blockchain REST API you want to query
            endpoint: The blockchain resource endpoint (refer to https://sawtooth.hyperledger.org/docs/core/releases/1.0/architecture/rest_api.html)
        Returns:
            A JSON dictionary of the response
        """
        SERVER_IP = '129.108.7.2'
        url = "http://" + SERVER_IP + ":" + str(api_port) + endpoint
        #print("URL requesting: " + url)
        r = requests.get(url)
        return r.json()

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
