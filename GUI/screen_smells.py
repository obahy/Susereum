# read the suse file for this, it is under
# D:\Users\AdEeL\Desktop\Practicum\GitHub-Repo\Susereum\Sawtooth\etc

import gi, time
import requests
import subprocess
import os
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

"""
Add code smells screen for Susereum.
Users can navigate to this screen after adding a new project in order to enter initial smells.
From this screen, after saving initial smell values, user is navigated back to the add project screen.
"""

class MainWindow(Gtk.Window):
    def __init__(self, url_, parent_):
        Gtk.Window.__init__(self, title="Smells")
        self.set_border_width(5)
        self.set_size_request(600, 300)
        self.set_resizable(False)
        self.url = url_
        self.parent = parent_

        r = requests.get(self.url)
        data = r.text.split('\n')
        self.prj_name = data[3]
        self.prj_id = data[4]
        self.api = data[2]
        self.suse_path = (os.environ['HOME'])+'/.sawtooth_projects/.' + self.prj_name + '_' + self.prj_id + '/etc/.suse'

        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(box_outer)

        # ListStore (lists that TreeViews can display) and specify data types
        projects_list_store = Gtk.ListStore(str, str)

        # Top Section
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        box_outer.pack_start(self.listbox, True, True, 0)

        self.row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.row.add(hbox)
        #self.tog_pro_act = Gtk.CheckButton("Proposal active days:")
        #self.tog_pro_act.set_active(True)
        #self.tog_pro_act.connect("toggled", self.on_tog_pro_act)
        self.lbl_pro_act = Gtk.Label('Proposal active days:')
        hbox.pack_start(self.lbl_pro_act, True, True, 0)
        self.txt_pro_act = Gtk.Entry()
        self.txt_pro_act.set_text("0")
        hbox.pack_start(self.txt_pro_act, False, True, 0)
        self.listbox.add(self.row)

        self.row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.row.add(hbox)
        #self.tog_app_tre = Gtk.CheckButton("Approval threshold:")
        #self.tog_app_tre.set_active(True)
        #self.tog_app_tre.connect("toggled", self.on_tog_app_tre)
        self.lbl_app_tre = Gtk.Label('Approval treshold:')
        hbox.pack_start(self.lbl_app_tre, True, True, 0)
        self.txt_app_tre = Gtk.Entry()
        self.txt_app_tre.set_text("0")
        hbox.pack_start(self.txt_app_tre, False, True, 0)
        self.listbox.add(self.row)

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
        self.listbox.add(self.row)

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
        self.listbox.add(self.row)

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
        self.listbox.add(self.row)

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
        self.listbox.add(self.row)

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
        self.listbox.add(self.row)

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
        self.listbox.add(self.row)

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
        self.listbox.add(self.row)

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
        self.listbox.add(self.row)

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
        self.listbox.add(self.row)

        # keep going if more rows are required.

        # Bottom section
        self.listbox_3 = Gtk.ListBox()
        self.listbox_3.set_selection_mode(Gtk.SelectionMode.NONE)
        box_outer.pack_start(self.listbox_3, False, True, 0)

        self.row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.row.add(hbox)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hbox.pack_start(vbox, True, True, 0)
        self.lbl_project = Gtk.Label('Update the code smells values for the project')
        vbox.pack_start(self.lbl_project, True, False, 0)

        self.button = Gtk.Button.new_with_label("Save")
        self.button.connect("clicked", self.save_smells)
        hbox.pack_start(self.button, False, True, 0)
        self.listbox_3.add(self.row)

        self.connect("delete-event", Gtk.main_quit)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.show_all()

    '''
    def on_tog_pro_act(self, tog_pro_act):
        self.txt_pro_act.set_sensitive(tog_pro_act.get_active())
        self.txt_pro_act.set_text("0")
        #print("Selected")

    def on_tog_app_tre(self, tog_app_tre):
        self.txt_app_tre.set_sensitive(tog_app_tre.get_active())
        self.txt_app_tre.set_text("0")
        #print("Selected")
    '''

    def on_tog_large_class(self, tog_large_class):
        """
          on_tog_large_class - ensures if the field is unchecked, set the value 0
          :param widget: widget
        """
        self.txt_large_class.set_sensitive(tog_large_class.get_active())
        self.txt_large_class.set_text("0")
        #print("Selected")

    def on_tog_small_class (self, tog_small_class):
        """
          on_tog_small_class - ensures if the field is unchecked, set the value 0
          :param widget: widget
        """
        self.txt_small_class.set_sensitive(tog_small_class.get_active())
        self.txt_small_class.set_text("0")
        #print("Selected")

    def on_tog_large_method(self, tog_large_method):
        """
          on_tog_large_method - ensures if the field is unchecked, set the value 0
          :param widget: widget
        """
        self.txt_large_method.set_sensitive(tog_large_method.get_active())
        self.txt_large_method.set_text("0")
        #print("Selected")

    def on_tog_small_method(self, tog_small_class):
        """
          on_tog_small_method - ensures if the field is unchecked, set the value 0
          :param widget: widget
        """
        self.txt_small_method.set_sensitive(tog_small_class.get_active())
        self.txt_small_method.set_text("0")
        #print("Selected")

    def on_tog_large_param(self, tog_large_param):
        """
          on_tog_large_param - ensures if the field is unchecked, set the value 0
          :param widget: widget
        """
        self.txt_large_param.set_sensitive(tog_large_param.get_active())
        self.txt_large_param.set_text("0")
        #print("Selected")

    def on_tog_god_class(self, tog_god_class):
        """
          on_tog_god_class - ensures if the field is unchecked, set the value 0
          :param widget: widget
        """
        self.txt_god_class.set_sensitive(tog_god_class.get_active())
        self.txt_god_class.set_text("0")
        #print("Selected")

    def on_tog_inapp_intm(self, tog_inapp_intm):
        """
          on_tog_inapp_intm - ensures if the field is unchecked, set the value 0
          :param widget: widget
        """
        self.txt_inapp_intm.set_sensitive(tog_inapp_intm.get_active())
        self.txt_inapp_intm.set_text("0")
        #print("Selected")

    def on_tog_ctc_up(self, tog_ctc_up):
        """
          on_tog_ctc_up - ensures if the field is unchecked, set the value 0
          :param widget: widget
        """
        self.txt_ctc_up.set_sensitive(tog_ctc_up.get_active())
        self.txt_ctc_up.set_text("0.0")
        #print("Selected")

    def on_tog_ctc_lw(self, tog_ctc_lw):
        """
          on_tog_ctc_lw - ensures if the field is unchecked, set the value 0
          :param widget: widget
        """
        self.txt_ctc_lw.set_sensitive(tog_ctc_lw.get_active())
        self.txt_ctc_lw.set_text("0.0")
        # self.button.connect("clicked", self.add_project, projects_list_store)
        # validate_float(txt_ctc_lw)
        #print("Selected")
    '''
    def add_project(self, widget, list_store):
        print("Adding project: " + str(self.txt_project.get_text()) + " " + self.get_time_date())
        x = [str(self.txt_large_class.get_text()), self.get_time_date()]
        list_store.append(x)
    '''
    def load_suse(self):
        """
          load_suse - load the existing suse file
        """
        #TODO change default vals
        suse = open(self.suse_path,'r')

    def save_to_suse(self):
        """
          save_to_suse - create the suse file, fetch smells data from the GUI fields
        """
        #read vars from GUI
        smell = [str(self.txt_pro_act.get_text()),
                 str(self.txt_app_tre.get_text()),
                 str(self.txt_large_class.get_text()),
                 str(self.txt_god_class.get_text()),
                 str(self.txt_small_class.get_text()),
                 str(self.txt_inapp_intm.get_text()),
                 str(self.txt_ctc_up.get_text()),
                 str(self.txt_ctc_lw.get_text()),
                 str(self.txt_large_method.get_text()),
                 str(self.txt_large_param.get_text()),
                 str(self.txt_small_method.get_text())]
        #TODO validate input

        #write to suse
        suse = open(self.suse_path, 'w')
        suse.write('''# Copyright 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

#
# Sawtooth -- Settings Transaction Processor Configuration
#\n''')
        suse.write('[about]'+'\n')
        suse.write('NewuserLink = "'+self.url+'"'+'\n')
        suse.write('Title = "Code Smell Family Configuration"'+'\n')
        suse.write('\n')
        suse.write('[vote_setting]'+'\n')
        suse.write('proposal_active_days = ['+smell[0]+',1,]\n')
        suse.write('approval_treshold = ['+smell[1]+',1,]\n')
        suse.write('\n')
        suse.write('[code_smells.class]'+'\n')
        suse.write('LargeClass = ['+smell[2]+',1,]\n')
        suse.write('GodClass = ['+smell[3]+',1,]\n')
        suse.write('SmallClass = ['+smell[4]+',1,]\n')
        suse.write('InappropriateIntimacy = ['+smell[5]+',1,]\n')
        suse.write('\n')
        suse.write('[code_smells.comments]'+'\n')
        suse.write('CommentsToCodeRatioUpper = ['+smell[6]+',1.0,]\n')
        suse.write('CommentsToCodeRatioLower = ['+smell[7]+',1.0,]\n')
        suse.write('\n')
        suse.write('[code_smells.method]'+'\n')
        suse.write('LargeMethod = ['+smell[8]+',1,]\n')
        suse.write('LargeParameterList = ['+smell[9]+',1,]\n')
        suse.write('SmallMethod = ['+smell[10]+',1,]\n')
        suse.close()

    def save_smells(self, widget):
        """
          save_smells - getting the new smell values from the GUI and save them for the selected project
          :param widget: widget
        """
        self.save_to_suse()
        print("Adding project: " + self.prj_name + " " + self.get_time_date())
        x = [self.prj_name, self.get_time_date()]
        self.parent.list_store.append(x)
        #TODO call github to update .suse

        #Call chain to update existing clients
        print('RUNING:',(['./smell.sh',str(self.api),((os.environ['HOME'])+'/.sawtooth_projects/.' + self.prj_name + '_' + self.prj_id )]))
        subprocess.Popen(['./smell.sh',str(self.api),((os.environ['HOME'])+'/.sawtooth_projects/.' + self.prj_name + '_' + self.prj_id )])

        #os.spawnl(os.P_DETACH, 'python3 ../Sawtooth/bin/code_smells.py default --connect http:127.0.0.1:'+str(self.api)+' --path '+('~/.sawtooth_projects/' + self.prj_name + '_' + self.prj_id ))
        # TODO close self
        try:
            self.destroy()
        except:
            pass
        #from screen_2 import MainWindow
        #win = MainWindow()
        ##var1.show()

    def get_time_date(self):
        """
          add_vote - to add the vote
          :returns: timestamp
        """
        return time.strftime("%m-%d-%Y %H:%M")

    def validate_float(self, widget, entry):
        """
          validate_float - method to validate the text field entry if it is other than integers or float values
          :param widget: widget
        """
        entry_text = entry.get_text()
        newtext = self.rx.findall(entry_text)
        if len(newtext):
            entry.set_text(newtext[0])
        else:
            entry.set_text("")


if __name__ == '__main__':
    window = MainWindow()
    window.connect("delete-event", Gtk.main_quit)
    window.set_position(Gtk.WindowPosition.CENTER)
    window.show_all()
    Gtk.main()
