from tkinter import *
from odf_query import *
from app_tools import *
from app_selector import *
from app_dictionary import _, load_dictionary

class AppFilter(Toplevel):
    """Window for managing a filter (for adding or modifying a filter)
    
    Arguments:
        Toplevel {Toplevel (tkinter)} -- Window preventing actions on other windows
    """
    def __init__(self, federation=None, app_parent=None, query_filters=[], query_tables=[], filter_index=None):
        """Constructor of the AppFilter class
        
        Keyword Arguments:
            federation {Federation} -- Federation of the filter (default: {None})
            app_parent {Frame (tkinter)} -- parent window (default: {None})
            query_filters {list} -- list of the query filters (default: {[]})
            query_tables {list} -- tables used in the query (default: {[]})
            filter_index {int} -- filter index for update (default: {None})
        """
        Toplevel.__init__(self)
        self.federation = federation
        self.app_parent = app_parent
        self.query_filters = query_filters
        self.query_tables = query_tables
        self.filter_index = filter_index
        self.display_values_label = None
        self.values_listbox = None

        """ Sources list """
        filter_label = label_frame(self, _("SELECT A FIELD TO FILTER"), x=0, y=0)
        self.app_sel = AppSelector(filter_label, federation=self.federation, tables_list=self.query_tables,
                                    fct_select=self.maj_field_to_filter, select_button="v")
        bind_evt("dclick", self.app_sel.fields_list, self.maj_field_to_filter)
        """ FIELD TO FILTER """  
        field_to_filter_label = label_frame(filter_label, _("FIELD TO FILTER"), x=2, y=0)
        self.field_to_filter = entry(field_to_filter_label, "", width_entry=40, x=0, y=0, disable=True)
        
        """ Operators list """
        filter_type_label = label_frame(self, _("Operator :"), x=0, y=1)
        self.filter_types_list = list_box(filter_type_label, vbar=True, hbar=False, x=0, y=1, width=15, height=10)
        button(filter_type_label, "=>", self.maj_filter_type, x=0, y=3)
        operators = ["=", ">", ">=", "<", "<=", "IN", "NOT IN", "BETWEEN", "NOT BETWEEN", "LIKE", "NOT LIKE"] 
        i=0
        for operator in operators:
            self.filter_types_list.insert(i, operator)
            i += 1
        bind_evt("dclick", self.filter_types_list, self.maj_filter_type)
        self.filter_type = entry(filter_type_label, "",  width_entry=15, x=1, y=1, disable=True)
        """ For update """
        if self.filter_index != None:
            if self.query_tables == []:
                self.app_sel.tables_listbox.insert(0,self.query_filters[self.filter_index].field.table.target_name)
                self.app_sel.fields_list.insert(0, self.query_filters[self.filter_index].field.field_name)
            self.field_to_filter[0].set("{}.{}".format(self.query_filters[self.filter_index].field.table.target_name, self.query_filters[self.filter_index].field.field_name)) 
            self.saved_field_to_filter = self.query_filters[self.filter_index].field
            self.filter_type[0].set(self.query_filters[self.filter_index].filter_type)
            self.display_values_selection()
        self.grab_set()
    
    def maj_field_to_filter(self,evt=None):
        """Set the field to filter
        
        Keyword Arguments:
            evt {Event} -- event (default: {None})
        """
        if self.display_values_label != None:
            self.display_values_label.destroy() 
        for index in self.app_sel.fields_list.curselection():
            print(self.app_sel.fields_tab[index].field_name)
            self.field_to_filter[0].set("{}.{}".format(self.app_sel.fields_tab[index].table.target_name,
                                            self.app_sel.fields_tab[index].field_name))
            self.saved_field_to_filter = self.app_sel.fields_tab[index]
        
    def maj_filter_type(self,evt=None):
        """Set the operator to use in the filter
        
        Keyword Arguments:
            evt {Event} -- event (default: {None})
        """
        try:
            for index in self.filter_types_list.curselection():
                print(self.filter_types_list.get(index))
                self.filter_type[0].set(self.filter_types_list.get(index))
                self.saved_filter_type = self.filter_types_list.get(index)
                self.display_values_selection()
        except:
            msg(_("Warning"), _("Select a field"), type="warning")

    def save_filter(self):
        """Create the filter and add it in the filters list of the query
        """
        if self.filter_index != None:
            del self.query_filters[self.filter_index] 
            self.app_parent.filters_list.delete(self.filter_index, self.filter_index)
        selected_values = []
        warning = False
        if self.filter_type[0].get() in ["BETWEEN", "NOT BETWEEN"]:
            selected_values.append(self.value1[0].get())
            selected_values.append(self.value2[0].get())
            if self.value1[0].get() == "" or self.value2[0].get() == "":
                warning = True
        elif self.filter_type[0].get() in ["LIKE", "NOT LIKE"]:
            selected_values.append(self.like_value[0].get())
            if self.like_value[0].get() == "":
                warning = True
        else:
            for index in self.values_listbox.curselection():
                selected_values.append(str(self.values_listbox.get(index)[0]))
            if selected_values == []:
                warning = True
        if warning:
            msg(_("Warning"), _("Select value(s)"), type="warning")
        else:
            print(selected_values)
            filter = Filter(self.saved_field_to_filter, self.filter_type[0].get(), selected_values)
            self.query_filters.append(filter)
            self.app_parent.filters_list.insert(self.app_parent.filters_list.size(), filter.description)
            self.destroy()
        
    def delete_filter(self):
        """Delete and remove the filter from the filters list of the query
        """
        try:
            del self.query_filters[self.filter_index]           
            self.app_parent.filters_list.delete(self.filter_index, self.filter_index)
            self.destroy()
        except:
            print(_("Error"))

    def display_values_selection(self):
        """Display values of the selected field
        """
        if self.display_values_label != None:
           self.display_values_label.destroy() 
        self.display_values_label = label_frame(self, _("SELECT OR ENTER VALUE(S)"), x=0, y=2)
        fields = [QueryField(self.saved_field_to_filter.table, self.saved_field_to_filter.field_name)]
        values_list = Query(self.federation, fields, [], [], limit=100, agregate=True)
        values_list.execute()
        values_list = values_list.query_result        
        if self.filter_type[0].get() in ["=", ">", ">=", "<", "<="]:
            self.values_listbox = list_box(self.display_values_label, vbar=True, hbar=True, 
                                        width=20, height=20, values=values_list)
        elif self.filter_type[0].get() in ["IN", "NOT IN"]:
            self.values_listbox = list_box(self.display_values_label, vbar=True, hbar=True, 
                                        width=20, height=20, values=values_list, selectmode="multiple")
        elif self.filter_type[0].get() in ["BETWEEN", "NOT BETWEEN"]:
            self.value1 = entry(self.display_values_label, "",  width_entry=15)
            label(self.display_values_label, " AND ", y=1)
            self.value2 = entry(self.display_values_label, "",  width_entry=15, y=2)
        elif self.filter_type[0].get() in ["LIKE", "NOT LIKE"]:
            self.like_value = entry(self.display_values_label, _("Character string"),  width_entry=15, x=1, y=1)
        if self.filter_index != None:
            i = 0
            for index in range(0, self.values_listbox.size()):
                if str(self.values_listbox.get(i)[0]) in self.query_filters[self.filter_index].filter_values:
                    self.values_listbox.selection_set(i)
                i += 1
            button(self.display_values_label, _("Modify filter"), self.save_filter, x=1)
            button(self.display_values_label, _("Remove filter"), self.delete_filter, x=2)
        else:
            """ Validation button """
            button(self.display_values_label, _("Add filter"), self.save_filter, x=1)

