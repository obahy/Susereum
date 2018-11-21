import gi, os
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

"""
Login Screen for Susereum.
Uses GitHub Credentials to Authenticate user
User can navigate to add project screen after sucessful login
"""

class UserInput(Gtk.Window):
  def __init__(self):
    Gtk.Window.__init__(self, title="Login Susereum")
    self.set_border_width(5)
    self.set_size_request(300, 100)
    self.set_resizable(False)

    # Layout
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    self.add(vbox)

    # Username
    self.username = Gtk.Entry()
    self.username.set_text("Username")
    self.username.connect("activate", self.sign_in)  # hit signin when enter is pressed
    vbox.pack_start(self.username, True, True, 0)

    # Password
    self.password = Gtk.Entry()
    self.password.set_text("P@ssw0rd")
    self.password.set_visibility(False)
    self.password.connect("activate", self.sign_in)#hit signin when enter is pressed
    vbox.pack_start(self.password, True, True, 0)

    # Sign In Button
    self.btn_signin = Gtk.Button(label="Sign In")
    self.btn_signin.connect("clicked", self.sign_in)
    vbox.pack_start(self.btn_signin, True, True, 0)

    # Cancel Button
    self.btn_cancel = Gtk.Button(label="Cancel")
    self.btn_cancel.connect("clicked", self.cancel)
    vbox.pack_start(self.btn_cancel, True, True, 0)

  def hit_enter(self, widget):
    """
      User hitting Enter in the user name or password screen
      :param widget: widget
    """
    print("Hit Enter")

  def sign_in(self, widget):
    """
      Sign in - btn_signin action.
      :param widget: widget
    """
    #TODO: User authentication from Github
    

    if(self.username.get_text()=='Admin' and self.password.get_text()=='P@ssw0rd'):
      print("login sucessful")
      from screen_add_project import MainWindow
      win = MainWindow()
      self.destroy()

    else:
      print("Invalid user name or password")

  def cancel(self, widget):
    """

    :param widget:
    :return:
    """
    print("Thank you.")
    self.destroy()

window = UserInput()
window.connect("delete-event", Gtk.main_quit)
window.set_position(Gtk.WindowPosition.CENTER)
window.show_all()
Gtk.main()
