from tkinter import *
import tkinter.filedialog
from odf_query import *
from app_tools import *
from app_result import *
from app_dictionary import _, load_dictionary


class AppSelector(Frame):
    
    def __init__(self, parent=None, federation=None, tables_list=[], app_federation=None, app_query=None, 
                x=0, y=0, modify_source=False, fct_select=None, select_button="", refresh=False):
        Frame.__init__(self, parent, padx=5, pady=0)
        self.grid(row=x, column=y)
        self.window = parent
        self.app_federation = app_federation
        self.app_query = app_query
        self.federation = federation
        self.tables_list = tables_list
        self.modify_source = modify_source
        """ Liste des sources """
        if tables_list == []:
            sources_label = label_frame(self, _("Sources"))
            if refresh == True:
                self.refresh_button = button(sources_label, _("Refresh"), self.source_refresh, x=0, y=1)
            self.sources_list = list_box(sources_label, vbar=True, hbar=True, x=1, y=0, width=45, height=6)
            bind_evt("click", self.sources_list, self.maj_tables_list)
            if self.modify_source == True:    
                bind_evt("dclick", self.sources_list, self.app_federation.modify_source)

            """ Alimentation des sources """
            i = 0
            for source in self.federation.sources:
                self.sources_list.insert(i,source.name)
                i += 1
            i = 0
        """ Liste des tables """
        label_tables_fields = label_frame(self, _("Tables - Fields"), x=1, y=0)
        label(label_tables_fields, _("Tables"), 0, 0)
        self.tables_listbox = list_box(label_tables_fields, vbar=True, hbar=True, x=1, y=0, height=8)
        bind_evt("click", self.tables_listbox, self.maj_fields_list)
        """ Alimentation de la liste des tables """
        if tables_list != []:
            i = 0
            self.tables_tab = []
            for table in tables_list:
                self.tables_listbox.insert(i, table.target_name)
                self.tables_tab.append(table)
                i += 1
        else:
            self.tables_tab = []
        """ Liste des champs """
        label(label_tables_fields, _("Fields"), 0, 2)
        self.fields_list = list_box(label_tables_fields, vbar=True, hbar=True, x=1, y=2, height=8)
        frame = Frame(label_tables_fields)
        frame.grid(row=1, column=4)
        if select_button != "":
            if fct_select != None:
                button(frame, select_button, fct_select, x=0, y=0)
                bind_evt("dclick", self.fields_list, fct_select)
            else:
                button(frame, select_button, self.maj_query_fields, x=0, y=0)
                bind_evt("dclick", self.fields_list, self.maj_query_fields)
        else:
            bind_evt("dclick", self.fields_list, self.maj_query_fields)
        button(frame, "?", self.view_field, x=1, y=0)
        
        
    def maj_tables_list(self,evt):
        #try:
        self.tables_listbox.delete(0,self.tables_listbox.size())
        self.fields_list.delete(0,self.fields_list.size())
        for index in self.sources_list.curselection():
            i=0
            self.source_table = []
            for table in self.federation.sources[index].tables:
                self.tables_listbox.insert(i,table.table_name)
                self.source_table.append("{}{}".format(table.source.type, table.source.id))
                i+=1
        #except:
        #    print("erreur")

    def maj_fields_list(self,evt):
        #try:
        self.fields_list.delete(0,self.fields_list.size())
        for index in self.tables_listbox.curselection():
            
            self.fields_tab = []
            if self.tables_list == []:
                fields = self.federation.sources_name[self.source_table[index]].tables[index].fields
            else:
                fields = self.tables_tab[index].fields
            self.fields_list.insert(0, "*")
            self.fields_tab.append("*")
            i=1
            for field in fields:
                self.fields_list.insert(i,field.field_name)
                self.fields_tab.append(field)
                print("index : {} - {}".format(i,field.field_name))
                print("tab : {}".format(self.fields_tab[i]))
                i+=1
        #except:
        #    print("erreur")

    def maj_query_fields(self, evt=None):
        #try:
        self.app_query.query_fields_list.delete(0,self.app_query.query_fields_list.size())
        for index in self.app_federation.app_sel.fields_list.curselection():
            print("index : {}".format(index))
            if index == 0:
                for i in range(1, len(self.app_federation.app_sel.fields_tab)):
                    self.app_query.query_fields_app.append(QueryField(self.app_federation.app_sel.fields_tab[i].table, 
                                                    self.app_federation.app_sel.fields_tab[i].field_name))
            else:
                self.app_query.query_fields_app.append(QueryField(self.app_federation.app_sel.fields_tab[index].table, 
                                                    self.app_federation.app_sel.fields_tab[index].field_name))
        #self.app_query.query_fields_app = list(set(self.app_query.query_fields_app))
        #self.app_query.query_fields_app = list(dict().fromkeys(self.app_query.query_fields_app).keys())
        query_fields_app = []
        field_dict = {}
        i = 0
        for field1 in self.app_query.query_fields_app:
            for field2 in self.app_query.query_fields_app:
                if "{}.{}".format(field1.table.target_name, field1.field_name) == "{}.{}".format(field2.table.target_name, field2.field_name):
                    try:
                        field_dict[field1.table.target_name, field1.field_name] += 1
                    except:
                        field_dict[field1.table.target_name, field1.field_name] = 1
                    if field_dict[field1.table.target_name, field1.field_name] == 1:
                        query_fields_app.append(self.app_query.query_fields_app[i])
            i += 1
        self.app_query.query_fields_app = query_fields_app
        #print(self.app_query.query_fields_app)
        for field in self.app_query.query_fields_app:
            label = field.field_label()
            self.app_query.query_fields_list.insert(self.app_query.query_fields_list.size(), label)
        """ Ajout des jointures de la federation """
        joins = self.federation.find_joins(self.app_query.query_fields_app)
        self.app_query.query_joins = []
        self.app_query.joins_list.delete(0,self.app_query.joins_list.size())
        for join in joins:
            self.app_query.joins_list.insert(self.app_query.joins_list.size(), join.name)
            self.app_query.query_joins.append(join)
        #except:
        #    print("erreur")

    def view_field(self):
        
        for index in self.fields_list.curselection():
            fields = [QueryField(self.fields_tab[index].table, self.fields_tab[index].field_name)]
            view_query = Query(self.federation, fields, [], [], limit=100, agregate=True)
            view_query.execute()
        table_result = ResultDisplay(view_query.query_name, view_query.query_result, view_query.field_labels())
    
        #msg("Error", "Select a field", type="error", command_true=None, command_false=None)
        #msg("Error", "Select a field", type="error")
        pass

    def source_refresh(self):
        for index in self.sources_list.curselection():
            self.federation.sources[index].add_table_to_list()
            self.maj_tables_list(None)