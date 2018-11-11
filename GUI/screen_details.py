import gi
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
		self.page1.add(Gtk.Label('Project 1 \nProject 2 \nProject 3 \nProject 4 \nProject 5 \nProject 6'))
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
		
	def add_project(self, widget):
		print("Analyzing project: "+ str(self.url_path.get_text()))

	def create_project(self, widget):
		print("Creating project: "+ str(self.project_path.get_text()))		
		
window = MainWindow()
window.connect("delete-event", Gtk.main_quit)
window.set_position(Gtk.WindowPosition.CENTER)
window.show_all()
Gtk.main()