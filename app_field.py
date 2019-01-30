from tkinter import *
from app_tools import *
from app_selector import *
from app_dictionary import _, load_dictionary

class AppField(Toplevel):
    """Window object for managing a field to fill an alias or to define a function
    
    Arguments:
        Toplevel {Toplevel (tkinter)} -- Window blocking actions on other windows
    """
    def __init__(self, query_field, app_parent=None, query_field_index=None):
        """Constructor of the AppField class
        
        Arguments:
            query_field {QueryField} -- QueryField object
        
        Keyword Arguments:
            app_parent {Frame} -- parent object (default: {None})
            query_field_index {int} -- Field index to modify (default: {None})
        """
        Toplevel.__init__(self)
        self.query_field = query_field
        self.app_parent = app_parent
        self.query_field_index = query_field_index
        self.functions_list = None
        self.function_entry = None
        """ Field informations """
        infos_field = label_frame(self, _("Field informations"), x=0, y=0)
        label(infos_field, _("Source field :"), x=0, y=0)
        label(infos_field, 
              "{}.{}".format(self.query_field.table.target_name, self.query_field.field_name), 
              x=0, y=1)
        self.alias_entry = entry(infos_field, "Alias", x=1) 
        if self.query_field.alias != "":
            self.alias_entry[0].set(self.query_field.alias)
        """ Agregation """
        self.agregate_infos = label_frame(self, _("Agregation"), x=1, y=0)
        """ Types list"""
        self.field_type_label = label_frame(self.agregate_infos, _("Field type"), x=0, y=0)
        self.field_type_list = list_box(self.field_type_label, vbar=False, hbar=False, x=0, y=0, 
                selectmode="single", values=["AXYS", "VALUE"])
        bind_evt("dclick", self.field_type_list, self.maj_field_type)
        self.field_type_entry = entry(self.field_type_label, "", x=1, y=0, width_entry=10, disable=True)
        if self.query_field.field_type != "":
            self.field_type_entry[0].set(self.query_field.field_type)
            if self.query_field.field_type == "VALUE":
                self.display_functions()
            elif self.functions_list != None:
                self.functions_label.destroy()
        
        """ Save button """
        button(self, _("Save"), self.save_query_field, x=2, y=0)
        self.grab_set()

    def maj_field_type(self,evt):
        """Update field function
        
        Arguments:
            evt {Event} -- event
        """
        for index in self.field_type_list.curselection():
            self.field_type_entry[0].set(self.field_type_list.get(index))
        if  self.field_type_list.get(index) == "VALUE":
            self.display_functions()
        elif self.functions_list != None:
                self.functions_label.destroy()

    def maj_function(self,evt):
        """Update of the type of funtions (AVG, SUM, MAX,...)
        
        Arguments:
            evt {Event} -- event
        """
        for index in self.functions_list.curselection():
            self.function_entry[0].set(self.functions_list.get(index))
        if self.alias_entry[1].get() == "":
            self.alias_entry[0].set("{} of {}".format(self.function_entry[1].get(), self.query_field.field_name))
           
    def save_query_field(self):
        """Field save function
        """
        self.query_field.alias = self.alias_entry[1].get()
        self.query_field.field_type = self.field_type_entry[1].get()
        self.query_field.agregate_fct = ""
        if self.query_field.field_type == "VALUE":
            self.query_field.agregate_fct = self.function_entry[1].get()

        if self.app_parent != None and self.query_field_index != None:
            if self.query_field.agregate_fct != "":
                label = "{}({}.'{}') ".format(self.query_field.agregate_fct, 
                                              self.query_field.table.target_name, 
                                              self.query_field.field_name)
            else:
                label = "{}.{}".format(self.query_field.table.target_name, 
                                       self.query_field.field_name)
            if self.query_field.alias != "":
                label += " as <{}>".format(self.query_field.alias)
            self.app_parent.query_fields_list.delete(self.query_field_index, self.query_field_index)
            self.app_parent.query_fields_list.insert(self.query_field_index, label)
        self.destroy()

    def display_functions(self):
        """Display the types function 
        """
        self.functions_label = label_frame(self.agregate_infos, _("Function"), x=2, y=0)
        self.functions_list = list_box(self.functions_label, vbar=True, hbar=False, x=0, y=0, height=5, 
                selectmode="single", values=["AVG", "COUNT", "MAX", "MIN", "SUM"])
        bind_evt("dclick", self.functions_list, self.maj_function)
        self.function_entry = entry(self.functions_label, "", x=1, y=0, width_entry=10, disable=True)
        if self.query_field.agregate_fct != "":
            self.function_entry[0].set(self.query_field.agregate_fct)