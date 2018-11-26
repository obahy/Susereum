import gi
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import json
import subprocess
import os
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

"""
Project details screen for Susereum.
From the add project screen, user can select any particular existing project and navigate to this screen to see
the project overview. This screen also provides the additional functionality to add votes and proposals.
Existing smells can also be edited from this screen.
"""

class MainWindow(Gtk.Window):
	def __init__(self,path_):
		Gtk.Window.__init__(self, title="Susereum Home")
		self.set_border_width(5)
		self.set_size_request(600, 300)
		self.notebook = Gtk.Notebook()
		self.add(self.notebook)
		self.path = path_

		# TODO: Enable the following 2 lines later to do your thing Christian
		ports = open(self.path+'/etc/.ports').read()
		self.api = ports.split('\n')[2].strip()

		# First tab
		self.page1 = Gtk.Box()
		self.page1.set_border_width(10)
		#TODO thread health update
		'''
		healths = []
		myDates = []
		results = subprocess.check_output(['python3', '../Sawtooth/bin/health.py', 'list', '--type', 'health', '--url','http://127.0.0.1:'+str(self.api)])
		results = results.decode('utf-8').replace("'","\"").replace('": b"','": "').strip()
		dictionary = json.loads(results)
		for value in dictionary.values():
			data = value.split(',')#transaction_name,sender_id,health,status,time
			health = data[2]
			date = data[4].split('-') #[data[4][0:4],data[4][5:7],data[4][8:10],data[4][11:13],data[4][14:16],data[4][17:19]]
			healths.append(float(health))
			myDates.append(datetime(int(date[0]), int(date[1]), int(date[2]), int(date[3]), int(date[4]), int(date[5])))#TODO update to new date format?
			print(health,date)

		fig, ax = plt.subplots()
		ax.plot(myDates,healths,'ro')
		myfmt = DateFormatter("%y-%m-%d")
		ax.xaxis.set_major_formatter(myfmt)
		#ax.set_xlim(myDates[0], myDates[-1])
		ax.set_ylim(0, 100)
		## Rotate date labels automatically
		fig.autofmt_xdate()
		plt.xlabel("Date")
		plt.ylabel("Health")
		plt.title("Health per Commit")
		plt.yticks(np.arange(0,100,11))#TODO make dynamic
		#plt.xticks(None,1)#TODO make dynamic
		#plt.locator_params(axis='y',numticks=3)
		#plt.show()
		#plt.plot(healths,times,'ro')
		#plt.axis(['Mon','Tues','Wed'])
		plt.savefig('health.png')'''
		img = Gtk.Image.new_from_file("health.png") #TODO update this periodically and check for blank
		self.page1.add(img)

		self.notebook.append_page(self.page1, Gtk.Label('Health'))

		# Second tab
		self.page2 = Gtk.Box()
		self.page2.set_border_width(10)
		# TODO: Enable the following 2 lines later to do your thing Christian
		self.suse = open(self.path+'/etc/.suse','r').read()
		self.page2.add(Gtk.Label(self.suse))
		self.notebook.append_page(self.page2, Gtk.Label('Smells'))

		# Third tab
		self.page3 = Gtk.Box()
		self.page3.set_border_width(10)

		box_vote = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		self.page3.add(box_vote)

		# Top Section
		self.listbox_vot_v1 = Gtk.ListBox()
		self.listbox_vot_v1.set_selection_mode(Gtk.SelectionMode.NONE)
		box_vote.pack_start(self.listbox_vot_v1, False, True, 0)

		self.row = Gtk.ListBoxRow()
		hbox_lb1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		self.row.add(hbox_lb1)
		self.btn_accept = Gtk.Button.new_with_label("Accept Proposal")
		self.btn_accept.connect("clicked", self.accept_proposal)
		hbox_lb1.pack_start(self.btn_accept, True, True, 0)
		self.btn_reject = Gtk.Button.new_with_label("Reject Proposal")
		self.btn_reject.connect("clicked", self.reject_proposal)
		hbox_lb1.pack_start(self.btn_reject, True, True, 0)
		self.listbox_vot_v1.add(self.row)

		# Middle Section
		self.listbox_vot_v2 = Gtk.ListBox()
		self.listbox_vot_v2.set_selection_mode(Gtk.SelectionMode.NONE)
		box_vote.pack_start(self.listbox_vot_v2, False, True, 0)

		self.row = Gtk.ListBoxRow()
		hbox_lb2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
		self.row.add(hbox_lb2)
		vbox_lb2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		hbox_lb2.pack_start(vbox_lb2, True, True, 0)
		self.lbl_accept = Gtk.Label('Overall acceptance:')
		vbox_lb2.pack_start(self.lbl_accept, True, True, 0)

		self.txt_accept = Gtk.Entry()
		self.txt_accept.set_text("0000")
		self.txt_accept.set_sensitive(False)
		hbox_lb2.pack_start(self.txt_accept, True, True, 0)

		self.listbox_vot_v2.add(self.row)

		# Bottom Section
		self.listbox_vot_v3 = Gtk.ListBox()
		self.listbox_vot_v3.set_selection_mode(Gtk.SelectionMode.NONE)
		box_vote.pack_start(self.listbox_vot_v3, True, True, 0)

		self.row = Gtk.ListBoxRow()
		hbox_lb3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
		self.row.add(hbox_lb3)
		vbox_lb3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		hbox_lb3.pack_start(vbox_lb3, True, True, 0)
		self.lbl_reject = Gtk.Label('Overall rejection:')
		vbox_lb3.pack_start(self.lbl_reject, True, True, 0)

		self.txt_reject = Gtk.Entry()
		self.txt_reject.set_text("0000")
		self.txt_reject.set_sensitive(False)
		hbox_lb3.pack_start(self.txt_reject, False, True, 0)

		self.listbox_vot_v3.add(self.row)

		self.notebook.append_page(self.page3, Gtk.Label('Vote'))

		# 4th tab
		self.page4 = Gtk.Box()
		self.page4.set_border_width(10)

		box_proposal = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		self.page4.add(box_proposal)

		self.listbox_pro_1 = Gtk.ListBox()
		self.listbox_pro_1.set_selection_mode(Gtk.SelectionMode.NONE)
		box_proposal.pack_start(self.listbox_pro_1, False, True, 0)

		self.row = Gtk.ListBoxRow()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		self.row.add(hbox)
		self.lbl_pro_act = Gtk.Label('Proposal active days:')
		hbox.pack_start(self.lbl_pro_act, True, True, 0)
		self.txt_pro_act = Gtk.Entry()
		self.txt_pro_act.set_text("0")
		hbox.pack_start(self.txt_pro_act, False, True, 0)
		self.listbox_pro_1.add(self.row)

		self.row = Gtk.ListBoxRow()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		self.row.add(hbox)
		self.lbl_app_tre = Gtk.Label('Approval treshold:')
		hbox.pack_start(self.lbl_app_tre, True, True, 0)
		self.txt_app_tre = Gtk.Entry()
		self.txt_app_tre.set_text("0")
		hbox.pack_start(self.txt_app_tre, False, True, 0)
		self.listbox_pro_1.add(self.row)

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
		self.listbox_pro_1.add(self.row)

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
		self.listbox_pro_1.add(self.row)

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
		self.listbox_pro_1.add(self.row)

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
		self.listbox_pro_1.add(self.row)

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
		self.listbox_pro_1.add(self.row)

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
		self.listbox_pro_1.add(self.row)

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
		self.listbox_pro_1.add(self.row)

		self.row = Gtk.ListBoxRow()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		self.row.add(hbox)
		self.tog_ctc_up = Gtk.CheckButton("Comments to code ratio [upper]:")
		self.tog_ctc_up.set_active(True)
		self.tog_ctc_up.connect("toggled", self.on_tog_ctc_up)
		hbox.pack_start(self.tog_ctc_up, True, True, 0)
		self.txt_ctc_up = Gtk.Entry()
		self.txt_ctc_up.set_text("0.0")
		hbox.pack_start(self.txt_ctc_up, False, True, 0)
		self.listbox_pro_1.add(self.row)

		self.row = Gtk.ListBoxRow()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		self.row.add(hbox)
		self.tog_ctc_lw = Gtk.CheckButton("Comments to code ratio [lower]:")
		self.tog_ctc_lw.set_active(True)
		self.tog_ctc_lw.connect("toggled", self.on_tog_ctc_lw)
		hbox.pack_start(self.tog_ctc_lw, True, True, 0)
		self.txt_ctc_lw = Gtk.Entry()
		self.txt_ctc_lw.set_text("0.0")
		hbox.pack_start(self.txt_ctc_lw, False, True, 0)
		self.listbox_pro_1.add(self.row)

		# Bottom section
		self.listbox_pro_2 = Gtk.ListBox()
		self.listbox_pro_2.set_selection_mode(Gtk.SelectionMode.NONE)
		box_proposal.pack_start(self.listbox_pro_2, False, True, 0)

		self.row = Gtk.ListBoxRow()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
		self.row.add(hbox)
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		hbox.pack_start(vbox, True, True, 0)
		self.lbl_project = Gtk.Label('Update the code smells values for the project')
		vbox.pack_start(self.lbl_project, True, False, 0)

		self.btn_save = Gtk.Button.new_with_label("Save")
		hbox.pack_start(self.btn_save, False, True, 0)
		self.btn_save.connect("clicked", self.save_proposal)
		self.listbox_pro_2.add(self.row)

		self.row = Gtk.ListBoxRow()
		hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
		self.row.add(hbox)

		self.lbl_add_fields = Gtk.Label()
		self.lbl_add_fields.set_markup(
			"<a href=\"mailto:susereum@gmail.com\" title=\"Email Susereum@gmail.com\">Contact support (Susereum@gmail.com) to add more fields</a>")
		hbox.pack_start(self.lbl_add_fields, True, True, 0)
		self.listbox_pro_2.add(self.row)


		self.notebook.append_page(self.page4, Gtk.Label('Proposal'))

		# 5th tab
		self.page5 = Gtk.Box()
		self.page5.set_border_width(10)
		box_history = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		self.page5.add(box_history)

		# Required columns for History tab
		# we are ignoring URL from the Abel's comma seperated data. The fields are Type, Id, Data, State, URL and Date
		self.historical_data = [("Type 1", "ID 1", "Data 1", "State 1", "Date 1"),
						 ("Type 2", "ID 2", "Data 2", "State 2", "Date 2")]
		history_list_store = Gtk.ListStore(str, str, str, str, str)

		self.listbox_history = Gtk.ListBox()
		self.listbox_history.set_selection_mode(Gtk.SelectionMode.NONE)

		box_history.pack_start(self.listbox_history, True, True, 0)

		self.row = Gtk.ListBoxRow()

		hbox_history = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
		self.row.add(hbox_history)

		# # ListStore (lists that TreeViews can display) and specify data types
		# history_list_store = Gtk.ListStore(str, str)
		for item in self.historical_data:
			history_list_store.append(list(item))

		# x = ["hi", "test"]
		# history_list_store.append(x)

		#for row in history_list_store:
		#	print(row[:])  # Print all data

		# TreeView is the item that is displayed
		history_tree_view = Gtk.TreeView(history_list_store)
		# Enumerate to add counter (i) to loop

		# Testing new changes... [adding additional 2 columns]
		# for i, col_title in enumerate(["Project", "Date"]):
		for i, col_title in enumerate(["Type", "ID", "Data", "State", "Date"]):
			# Render means draw or display the data (just display as normal text)
			renderer = Gtk.CellRendererText()
			# Create columns (text is column number)
			column = Gtk.TreeViewColumn(col_title, renderer, text=i)
			# Make column sortable and selectable
			column.set_sort_column_id(i)
			# Add columns to TreeView
			history_tree_view.append_column(column)

		# Handle selection
		selected_row = history_tree_view.get_selection()
		#selected_row.connect("changed", self.item_selected)

		hbox_history.pack_start(history_tree_view, True, True, 0)

		self.listbox_history.add(self.row)



		self.notebook.append_page(self.page5, Gtk.Label('History'))
		self.set_position(Gtk.WindowPosition.CENTER)
		self.show_all()
		#Gtk.main()

	def accept_proposal(self, widget):
		"""
		  accept_proposal - to accept the proposal
		  :param widget: widget
		"""

		print("Accepting project")
		print("Rejecting project")
		proposal_id = subprocess.check_output(
			['python3', os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/Sawtooth/bin/code_smell.py',
			 'list', '--type', 'proposal', '--active', '1', '--url', 'http://127.0.0.1:' + self.api])
		proposal_id = proposal_id.decode('utf-8').split(' ')[0]
		print(['python3', os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/Sawtooth/bin/code_smell.py',
			   'vote','--id', proposal_id, '--vote', 'yes', '--url', 'http://127.0.0.1:' + self.api])
		subprocess.Popen(
			['python3', os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/Sawtooth/bin/code_smell.py',
			 'vote', '--id', proposal_id, '--vote', 'yes', '--url', 'http://127.0.0.1:' + self.api])
		#TODO make file so i cant vote again

	def reject_proposal(self, widget):
		"""
		  reject_proposal - to reject the proposal
		  :param widget: widget
		"""
		print("Rejecting project")
		proposal_id = subprocess.check_output(
			['python3', os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/Sawtooth/bin/code_smell.py', 'list',
			 '--type', 'proposal', '--active', '1', '--url', 'http://127.0.0.1:' + self.api])
		proposal_id = proposal_id.decode('utf-8').split(' ')[0]
		print(['python3', os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/Sawtooth/bin/code_smell.py', 'vote',
			 '--id', proposal_id, '--vote', 'no', '--url', 'http://127.0.0.1:' + self.api])
		subprocess.Popen(
			['python3', os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/Sawtooth/bin/code_smell.py', 'vote',
			 '--id', proposal_id, '--vote', 'no', '--url', 'http://127.0.0.1:' + self.api])
	# TODO make file so i cant vote again

	def save_proposal(self, widget):
		"""
		  save_proposal - to save the proposal
		  :param widget: widget
		"""
		print("Saving proposal")
		#TODO make proposal string
		proposal = "LargeClass="+str(self.txt_large_class.get_text())+","+"SmallClass="+str(self.txt_small_class.get_text())+","\
					+"GodClass="+str(self.txt_god_class.get_text())+","+"InappropriateIntimacy="+str(self.txt_inapp_intm.get_text())+","\
					+"LargeMethod="+str(self.txt_large_method.get_text())+","+"SmallMethod="+str(self.txt_small_method.get_text())+","\
					+"LargeParameterList="+str(self.txt_large_param.get_text())+","+"CommentsToCodeRatioLower="+str(self.txt_ctc_lw.get_text())+","\
					+"CommentsToCodeRatioUpper="+str(self.txt_ctc_up.get_text())
		subprocess.Popen(
			['python3', os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/Sawtooth/bin/code_smell.py', 'proposal',
			 '--propose', proposal, '--url', 'http://127.0.0.1:' + self.api])

	def on_tog_large_class(self, tog_large_class):
		"""
			on_tog_large_class - ensures if the field is unchecked, set the value 0
			:param widget: widget
		"""
		self.txt_large_class.set_sensitive(tog_large_class.get_active())
		self.txt_large_class.set_text("0")

	def on_tog_small_class(self, tog_small_class):
		"""
          on_tog_small_class - ensures if the field is unchecked, set the value 0
          :param widget: widget
		"""
		self.txt_small_class.set_sensitive(tog_small_class.get_active())
		self.txt_small_class.set_text("0")

	def on_tog_large_method(self, tog_large_method):
		"""
          on_tog_large_method - ensures if the field is unchecked, set the value 0
          :param widget: widget
		"""
		self.txt_large_method.set_sensitive(tog_large_method.get_active())
		self.txt_large_method.set_text("0")

	def on_tog_small_method(self, tog_small_class):
		"""
          on_tog_small_method - ensures if the field is unchecked, set the value 0
          :param widget: widget
		"""
		self.txt_small_method.set_sensitive(tog_small_class.get_active())
		self.txt_small_method.set_text("0")

	def on_tog_large_param(self, tog_large_param):
		"""
          on_tog_large_param - ensures if the field is unchecked, set the value 0
          :param widget: widget
		"""
		self.txt_large_param.set_sensitive(tog_large_param.get_active())
		self.txt_large_param.set_text("0")

	def on_tog_god_class(self, tog_god_class):
		"""
          on_tog_god_class - ensures if the field is unchecked, set the value 0
          :param widget: widget
		"""
		self.txt_god_class.set_sensitive(tog_god_class.get_active())
		self.txt_god_class.set_text("0")

	def on_tog_inapp_intm(self, tog_inapp_intm):
		"""
          on_tog_inapp_intm - ensures if the field is unchecked, set the value 0
          :param widget: widget
		"""
		self.txt_inapp_intm.set_sensitive(tog_inapp_intm.get_active())
		self.txt_inapp_intm.set_text("0")

	def on_tog_ctc_up(self, tog_ctc_up):
		"""
          on_tog_ctc_up - ensures if the field is unchecked, set the value 0
          :param widget: widget
		"""
		self.txt_ctc_up.set_sensitive(tog_ctc_up.get_active())
		self.txt_ctc_up.set_text("0.0")

	def on_tog_ctc_lw(self, tog_ctc_lw):
		"""
          on_tog_ctc_lw - ensures if the field is unchecked, set the value 0
          :param widget: widget
		"""
		self.txt_ctc_lw.set_sensitive(tog_ctc_lw.get_active())
		self.txt_ctc_lw.set_text("0.0")

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
