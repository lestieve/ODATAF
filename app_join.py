from tkinter import *
from odf_federation import *
from odf_query import *
from app_tools import *
from app_selector import *
from app_dictionary import _, load_dictionary

class AppJoin(Toplevel):
    """Window to manage the addition or modification of a join
    
    Arguments:
        Toplevel {Toplevel (tkinter)} -- Window preventing actions on other windows
    """
    def __init__(self, federation=None, app_parent=None, tables_list=[], joins=[], join_index=None):
        """Constructor of the AppJoin class
        
        Keyword Arguments:
            federation {Federation} -- data federation in which to add the join (default: {None})
            app_parent {Frame (tkinter)} -- parent window (default: {None})
            tables_list {list} -- List of tables that can be selected for the join (default: {[]})
            joins {list} -- list of joins in the data federation or query (default: {[]})
            join_index {int} -- join index to modify (default: {None})
        """
        Toplevel.__init__(self)
        self.federation = federation
        self.app_parent = app_parent
        self.tables_tab = []
        self.tables_list = tables_list
        self.joins = joins
        self.join_index = join_index

        """ List of sources on the left """
        left_key_label = label_frame(self, _("LEFT SIDE"), x=0, y=0)
        self.app_sel_left = AppSelector(left_key_label, federation=self.federation, tables_list=self.tables_list,
                                        fct_select=self.maj_left_key, select_button="v")
        bind_evt("dclick", self.app_sel_left.fields_list, self.maj_left_key)
        """ LEFT KEY """  
        left_key_lb = label_frame(left_key_label, _("LEFT KEY"), x=2, y=0)
        self.left_key = entry(left_key_lb, "", width_entry=40, x=0, y=0, disable=True)
        
        """ List of join types """
        join_type_label = label_frame(self, _("Join :"), x=0, y=1)
        label(join_type_label, _("JOIN TYPE"), x=0, y=1)
        self.join_types_list = list_box(join_type_label, vbar=False, hbar=False, x=1, y=1, width=15, height=3)
        self.join_types_list.insert(0, "INNER")
        self.join_types_list.insert(1, "LEFT")
        self.join_types_list.insert(2, "RIGHT")
        button(join_type_label, "v", self.maj_join_type, x=1, y=2)
        bind_evt("dclick", self.join_types_list, self.maj_join_type)
        self.join_type = entry(join_type_label, "",  width_entry=15, x=2, y=1, disable=True)
        """ List of sources on the right """
        right_key_label = label_frame(self, _("RIGHT SIDE"), x=0, y=2)
        self.app_sel_right = AppSelector(right_key_label, federation=self.federation, tables_list=self.tables_list,
                                         fct_select=self.maj_right_key, select_button="v")
        bind_evt("dclick", self.app_sel_right.fields_list, self.maj_right_key)
        """ RIGHT KEY """
        right_key_lb = label_frame(right_key_label, _("RIGHT KEY"), x=2, y=0)
        self.right_key = entry(right_key_lb, "", width_entry=40, x=0, y=0, disable=True)
        """ List of sources """
        """ Modification """
        if self.join_index != None:
            if self.tables_list == []:
                self.app_sel_left.tables_listbox.insert(0,self.joins[self.join_index].left_table_target)
                self.app_sel_right.tables_listbox.insert(0,self.joins[self.join_index].right_table_target)
            self.app_sel_left.fields_list.insert(0, self.joins[self.join_index].left_key)
            self.app_sel_right.fields_list.insert(0, self.joins[self.join_index].right_key)
            self.left_key[0].set("{}.{}".format(self.joins[self.join_index].left_table_target, self.joins[self.join_index].left_key)) 
            self.saved_left_key = self.federation.sources_name[self.joins[self.join_index].left_source].tables_name[self.joins[self.join_index].left_table].fields_name[self.joins[self.join_index].left_key]
            self.right_key[0].set("{}.{}".format(self.joins[self.join_index].right_table_target, self.joins[self.join_index].right_key)) 
            self.saved_right_key = self.federation.sources_name[self.joins[self.join_index].right_source].tables_name[self.joins[self.join_index].right_table].fields_name[self.joins[self.join_index].right_key]
            self.join_type[0].set(self.joins[self.join_index].join_type)
            button(join_type_label, _("Modify join"), self.modify_join, x=3, y=1)
            button(join_type_label, _("Remove join"), self.delete_join, x=4, y=1)
        else:
            """ Validation button """
            button(join_type_label, _("Add join"), self.save_join, x=3, y=1)
        self.grab_set()
    
    def maj_left_key(self,evt=None):
        """Add the selected left key
        
        Keyword Arguments:
            evt {Event} -- event (default: {None})
        """
        #try:
        for index in self.app_sel_left.fields_list.curselection():
            print(self.app_sel_left.fields_tab[index].field_name)
            self.left_key[0].set("{}.{}".format(self.app_sel_left.fields_tab[index].table.target_name,
                                            self.app_sel_left.fields_tab[index].field_name))
            self.saved_left_key = self.app_sel_left.fields_tab[index]
        #except:
        #    print("Error")

    def maj_right_key(self,evt=None):
        """Add the selected right key
        
        Keyword Arguments:
            evt {Event} -- event (default: {None})
        """
        try:
            for index in self.app_sel_right.fields_list.curselection():
                print(self.app_sel_right.fields_tab[index].field_name)
                self.right_key[0].set("{}.{}".format(self.app_sel_right.fields_tab[index].table.target_name,
                                            self.app_sel_right.fields_tab[index].field_name))
                self.saved_right_key = self.app_sel_right.fields_tab[index]
        except:
            print(_("Error"))

    def maj_join_type(self,evt=None):
        """Add the selected join type
        
        Keyword Arguments:
            evt {Event} -- event (default: {None})
        """
        try:
            for index in self.join_types_list.curselection():
                #self.join_type.set(str(self.join_types_list[index].getvar()))
                print(self.join_types_list.get(index))
                self.join_type[1].delete(0, END) 
                self.join_type[1].insert(0, self.join_types_list.get(index))
                self.join_type[0].set(self.join_types_list.get(index))
        except:
            print(_("Error"))

    def save_join(self):
        """Save and add the join in the joins list of the data federation or query.
        """
        #try:
        join = Join(self.saved_left_key.table.source.source_name, 
                    self.saved_left_key.table.table_name, 
                    self.saved_left_key.table.target_name, self.saved_left_key.field_name, 
                    self.saved_right_key.table.source.source_name, 
                    self.saved_right_key.table.table_name, 
                    self.saved_right_key.table.target_name, self.saved_right_key.field_name, 
                    self.join_type[0].get())
        self.joins.append(join)
        self.app_parent.joins_list.insert(self.app_parent.joins_list.size(), join.name)
        self.destroy()
        #except:
        #    msg("Warning", "Select left key, join type and right key", type="warning")

    def modify_join(self):
        """Modify a join
        """
        #try:
        del self.joins[self.join_index] 
        join = Join("{}{}".format(self.saved_left_key.table.source.type, self.saved_left_key.table.source.id), 
                    self.saved_left_key.table.table_name, 
                    self.saved_left_key.table.target_name, self.saved_left_key.field_name, 
                    "{}{}".format(self.saved_right_key.table.source.type, self.saved_right_key.table.source.id), 
                    self.saved_right_key.table.table_name, 
                    self.saved_right_key.table.target_name, self.saved_right_key.field_name, 
                    self.join_type[0].get())
        self.joins.insert(self.join_index, join)
        self.app_parent.joins_list.delete(self.join_index, self.join_index)
        self.app_parent.joins_list.insert(self.join_index, join.name)
        self.destroy()
        #except:
        #print("Error")

    def delete_join(self):
        """Delete a join
        """
        try:
            del self.joins[self.join_index]           
            self.app_parent.joins_list.delete(self.join_index, self.join_index)
            self.destroy()
        except:
            print(_("Error"))