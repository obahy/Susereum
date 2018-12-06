import gi
import numpy as np
#from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import json
import subprocess
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import requests     # Have to manually send requests to each blockchain REST API bc Sawtooth doesn't support 32-bit architecture
import base64
import os
import jwt
import datetime
import calendar

"""
Project details screen for Susereum explorer.
From the explorer screen, user can select any particuar existing project and navigate to this screen to see
the project overview. This screen also provides the additional functionality to view health and history details
"""

class MainWindow(Gtk.Window):

    def __init__(self, api_port):
        self.username_mappings = {}
        _get_environment_vars()
        self.api = api_port

        Gtk.Window.__init__(self, title="Explorer Details")
        self.set_border_width(5)
        self.set_size_request(800, 1000)
        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        # First tab
        healths = []
        myDates = []
        print(['python3', '../Sawtooth/bin/health.py', 'list', '--type', 'health', '--url',
               'http://127.0.0.1:' + str(self.api)])
        results = subprocess.check_output(['python3', '../Sawtooth/bin/health.py', 'list', '--type', 'health', '--url',
                                           'http://127.0.0.1:' + str(self.api)])
        if not results:
            pass
        else:
            results = results.decode('utf-8').replace("'", "\"").replace('": b"', '": "').strip()
            dictionary = json.loads(results)
            for value in dictionary.values():
                data = value.split(',')  # transaction_name,sender_id,health,status,time
                health = data[2]
                date = data[6].split(
                    '-')  # [data[4][0:4],data[4][5:7],data[4][8:10],data[4][11:13],data[4][14:16],data[4][17:19]]
                healths.append(float(health))
                print(date)
                myDates.append(datetime.datetime(int(date[0]),
                                        int(date[1]),
                                        int(date[2]),
                                        int(date[3]),
                                        int(date[4]),
                                        int(date[5])))
                print(health, date)

            fig, ax = plt.subplots()
            ax.plot(myDates, healths, 'ro')
            myfmt = DateFormatter("%y-%m-%d")
            ax.xaxis.set_major_formatter(myfmt)
            # ax.set_xlim(myDates[0], myDates[-1])
            ax.set_ylim(0, 100)
            ## Rotate date labels automatically
            fig.autofmt_xdate()
            plt.xlabel("Date")
            plt.ylabel("Health")
            plt.title("Health per Commit")
            plt.yticks(np.arange(0, 100, 10))  # TODO make dynamic
            # plt.xticks(None,1)#TODO make dynamic
            # plt.locator_params(axis='y',numticks=3)
            # plt.show()
            # plt.plot(healths,times,'ro')
            # plt.axis(['Mon','Tues','Wed'])
            plt.savefig('health.png')
            img = Gtk.Image.new_from_file("health.png")  # TODO update this periodically and check for blank

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

        # Get the authentication token ready to increase our rate limit
        _create_installation_token()

        try:
            for transaction in transactions['data']:
                payload = str(base64.b64decode(transaction['payload']))[2:-1]     # Returns base64 encoded comma-delimited payload
                payload_list = payload.split(',')
                transaction_type = payload_list[0]      # Transactions type is always the first item
                timestamp = payload_list[len(payload_list) - 1]  # Timestamp is always the last item

                sender_id = "Anonymous"
                if(transaction_type in ["commit", "health", "suse"]):
                    user_github_id = payload_list[1]
                    sender_id = self.github_user_id_to_username(user_github_id)
                    #sender_id = user_github_id

                # Filter out transactions
                if(transaction_type not in ["code_smell", "commit", "health", "proposal", "suse", "vote"]):
                    continue

                # Prepare labels for data, different transaction types have different labels
                if(transaction_type == "code_smell"):
                    data = "Code Smell: " + payload_list[1] + "\n"
                    data += "Values: " + payload_list[2] + "\n"
                    data += "State: " + payload_list[3] + "\n"
                elif (transaction_type == "commit"):
                    data = "GitHub ID: " + payload_list[1] + "\n"
                    data += "Commit URL: " + payload_list[2] + "\n"
                    data += "State: " + payload_list[3] + "\n"
                    data += "REST API URL: " + payload_list[4] + "\n"
                    data += "Peer IP: " + payload_list[5] + "\n"
                elif (transaction_type == "health"):
                    data = "GitHub ID: " + payload_list[1] + "\n"
                    data += "Health: " + payload_list[2] + "\n"
                    data += "State: " + payload_list[3] + "\n"
                    data += "Commit URL: " + payload_list[4] + "\n"
                    data += "IP Peer: " + payload_list[5] + "\n"
                elif (transaction_type == "proposal"):
                    data = "GitHub ID: " + payload_list[1] + "\n"
                    data += "Code Smells: " + self._beautify_code_smells(payload_list[2]) + "\n"
                    data += "State: " + payload_list[3] + "\n"
                elif(transaction_type == "suse"):
                    suse_transactions.append(transaction)       # To sum up the values
                    data = "GitHub ID: " + payload_list[1] + "\n"
                    data += "Suse: " + payload_list[2] + "\n"
                    data += "State: " + payload_list[3] + "\n"
                elif (transaction_type == "vote"):
                    data = "Vote ID: " + payload_list[1] + "\n"
                    data += "Proposal ID: " + payload_list[2] + "\n"
                    active = payload_list[3]
                    active = active.replace('0', 'closed').replace('1', 'active')
                    data += "State: " + active + "\n"
                else:
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
            payload = str(base64.b64decode(suse_transaction['payload']))[2:-1]     # Returns base64 encoded comma-delimited payload
            #print(payload)
            payload_list = payload.split(',')
            user_github_id = payload_list[1]
            user_github_username = self.github_user_id_to_username(user_github_id)
            #user_github_username = user_github_id
            suse_awarded = float(payload_list[2])

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
            #print(item)
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

    def _beautify_code_smells(self, code_smells):
        data = "\n"
        code_smells = code_smells.replace("'", '"').replace(";", ",")
        my_dict = json.loads(code_smells)
        for k, v in my_dict.items():
            data += "\t" + k + ": " + v + "\n"
        return data

    def github_user_id_to_username(self, id):
        global TOKEN

        username = ""
        if id in self.username_mappings:
            #print("Found a user in username mappings")
            username = self.username_mappings[id]
            return username

        try:
            headers = {'Authorization': ('Token ' + TOKEN)}		# Adds token to authorize as the Susereum bot
            url = "https://api.github.com/user/" + id
            r = requests.get(url, headers=headers)
            username = r.json()['login'].encode('ascii')     # unicode to ascii
            username = str(username)[2:-1]
            self.username_mappings[id] = username

            return username
        except:
            print("Problem trying to convert GitHub user id to username. You only have 5000 authenticated requests/hour.")
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

def _get_environment_vars():
    """
    Gets environment variables needed to verify
    and authenticate our app as a Susereum bot
    """
    global PRIVATE_KEY, APP_IDENTIFIER
    #PRIVATE_KEY_2 = os.getenv('GITHUB_PRIVATE_KEY')
    #APP_IDENTIFIER = os.getenv('GITHUB_APP_IDENTIFIER')
    file = open('private-key.pem', 'r')
    PRIVATE_KEY = file.read()
    file.close()
    APP_IDENTIFIER = "18490"

def _create_installation_token():
    """
    Generates token needed to authenticate Git API commands. You can send GitHub your JWT and installation ID
    and GitHub will return an authentication token.
    """
    global TOKEN

    JWT = _generate_JWT()
    installation_id = "363304"	# This can be found in a integration_installation_repositories payload
    URL = 'https://api.github.com/app/installations/'+installation_id+'/access_tokens'
    headers = {'Accept': 'application/vnd.github.machine-man-preview+json',
                'Authorization': ('Bearer ' + JWT)}
    raw_data = requests.post(URL, headers = headers)
    json_data = json.loads(raw_data.text)
    TOKEN = json_data['token']
    #print(TOKEN)
    return TOKEN

def _generate_JWT():
    """
    Creates a Json Web Token with a current time stamp and expiration time,
    and then uses it to create an authentication token
    """
    global PRIVATE_KEY, APP_IDENTIFIER
    current = datetime.datetime.utcnow()
    current_time = calendar.timegm(current.timetuple())

    future = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    expiration_time = calendar.timegm(future.timetuple())

    #print("Private key: " + PRIVATE_KEY)
    #print("App identifier: " + APP_IDENTIFIER)
    payload = {'iat': current_time, 'exp': expiration_time, 'iss': APP_IDENTIFIER}
    JWT = jwt.encode({'iat': current_time, 'exp': expiration_time, 'iss': APP_IDENTIFIER}, PRIVATE_KEY, algorithm='RS256')
    #print("JWT: " + str(JWT)[2:-1])
    return str(JWT)[2:-1]

if __name__ == '__main__':
    window = MainWindow()
    window.connect("delete-event", Gtk.main_quit)
    window.set_position(Gtk.WindowPosition.CENTER)
    window.show_all()
    Gtk.main()
