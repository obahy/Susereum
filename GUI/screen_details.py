# left a copy of existing code at the end, if something goes wrong, put it back!
import gi
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class MainWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="Susereum Home")
		self.set_border_width(5)
		self.set_size_request(600, 300)
		self.notebook = Gtk.Notebook()
		self.add(self.notebook)

		# First tab
		self.page1 = Gtk.Box()
		self.page1.set_border_width(10)
		healths = [50,60,70]
		myDates = [datetime(2012, 1, i + 3) for i in range(3)]

		fig, ax = plt.subplots()
		ax.plot(myDates,healths,'ro')
		myfmt = DateFormatter("%d")
		ax.xaxis.set_major_formatter(myfmt)
		ax.set_xlim(myDates[0], myDates[-1])
		## Rotate date labels automatically
		fig.autofmt_xdate()
		plt.xlabel("Date")
		plt.ylabel("Health")
		plt.title("Health per Commit")
		#plt.show()
		#plt.plot(healths,times,'ro')
		#plt.axis(['Mon','Tues','Wed'])
		plt.savefig('health.png')
		img = Gtk.Image.new_from_file("health.png")
		self.page1.add(img)

		self.notebook.append_page(self.page1, Gtk.Label('Health'))
		# Second tab
		self.page2 = Gtk.Box()
		self.page2.set_border_width(10)
		self.page2.add(Gtk.Label('Proposal 1 \nProposal 2 \nProposal 3 \nProposal 4'))
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
		self.txt_accept.set_text("display magic number")
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
		self.txt_reject.set_text("display magic number")
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
		box_proposal.pack_start(self.listbox_pro_1, True, True, 0)

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

		self.button = Gtk.Button.new_with_label("Save")
		hbox.pack_start(self.button, False, True, 0)
		self.listbox_pro_2.add(self.row)

		self.notebook.append_page(self.page4, Gtk.Label('Proposal'))

		self.connect("delete-event", Gtk.main_quit)
		self.set_position(Gtk.WindowPosition.CENTER)
		self.show_all()
		#Gtk.main()

	def accept_proposal(self, widget):
		print("Accepting project")

	def reject_proposal(self, widget):
		print("Rejecting project")


if __name__ == '__main__':
	window = MainWindow()
	window.connect("delete-event", Gtk.main_quit)
	window.set_position(Gtk.WindowPosition.CENTER)
	window.show_all()
	Gtk.main()

'''
import gi
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class MainWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="Susereum Home")
		self.set_border_width(5)
		self.set_size_request(600, 300)
		self.notebook = Gtk.Notebook()
		self.add(self.notebook)

		# First tab
		self.page1 = Gtk.Box()
		self.page1.set_border_width(10)
		healths = [50,60,70]
		myDates = [datetime(2012, 1, i + 3) for i in range(3)]

		fig, ax = plt.subplots()
		ax.plot(myDates,healths,'ro')
		myfmt = DateFormatter("%d")
		ax.xaxis.set_major_formatter(myfmt)
		ax.set_xlim(myDates[0], myDates[-1])
		## Rotate date labels automatically
		fig.autofmt_xdate()
		plt.xlabel("Date")
		plt.ylabel("Health")
		plt.title("Health per Commit")
		#plt.show()
		#plt.plot(healths,times,'ro')
		#plt.axis(['Mon','Tues','Wed'])
		plt.savefig('health.png')
		img = Gtk.Image.new_from_file("health.png")
		self.page1.add(img)

		self.notebook.append_page(self.page1, Gtk.Label('Health'))
		# Second tab
		self.page2 = Gtk.Box()
		self.page2.set_border_width(10)
		self.page2.add(Gtk.Label('Proposal 1 \nProposal 2 \nProposal 3 \nProposal 4'))
		self.notebook.append_page(self.page2, Gtk.Label('Smells'))

		# Third tab
		self.page3 = Gtk.Box()
		self.page3.set_border_width(10)
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		self.page3.add(vbox)
		self.lbl_project = Gtk.Label('Project URL or PATH')
		vbox.pack_start(self.lbl_project, True, True, 0)
		self.url_path = Gtk.Entry()
		vbox.pack_start(self.url_path, True, True, 0)
		self.btn_add = Gtk.Button('Analyze')
		self.btn_add.connect("clicked", self.add_project)
		vbox.pack_start(self.btn_add, True, True, 0)
		self.notebook.append_page(self.page3, Gtk.Label('Vote'))

		# 4th tab
		self.page4 = Gtk.Box()
		self.page4.set_border_width(10)
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		self.page4.add(vbox)
		self.lbl_project1 = Gtk.Label('Project')
		vbox.pack_start(self.lbl_project1, True, True, 0)
		self.project_path = Gtk.Entry()
		vbox.pack_start(self.project_path, True, True, 0)
		self.btn_create = Gtk.Button('Create')
		self.btn_create.connect("clicked", self.create_project)
		vbox.pack_start(self.btn_create, True, True, 0)
		self.notebook.append_page(self.page4, Gtk.Label('Proposal'))

		self.connect("delete-event", Gtk.main_quit)
		self.set_position(Gtk.WindowPosition.CENTER)
		self.show_all()
		#Gtk.main()

	def add_project(self, widget):
		print("Analyzing project: "+ str(self.url_path.get_text()))

	def create_project(self, widget):
		print("Creating project: "+ str(self.project_path.get_text()))		


if __name__ == '__main__':
	window = MainWindow()
	window.connect("delete-event", Gtk.main_quit)
	window.set_position(Gtk.WindowPosition.CENTER)
	window.show_all()
	Gtk.main()
'''