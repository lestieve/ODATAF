from tkinter import *
from app_tools import *
from app_selector import *
from app_dictionary import _, load_dictionary


class AppToSql(Toplevel):

    def __init__(self, query, app_parent=None):
        Toplevel.__init__(self)
        self.query = query
        self.label_query = None
        
        self.set_fields = []
        self.where_fields = []
        """ Field informations """
        self.sql_label = label_frame(self, _("SQL query"))
        label(self.sql_label, _("DB type :"))
        self.db_type_list = list_box(self.sql_label, vbar=True, hbar=False, x=1, 
                                        selectmode="single", values=["SQLITE", "MYSQL"])
        self.db_type = entry(self.sql_label, "", x=2, disable=True) 
        bind_evt("dclick", self.db_type_list, self.maj_db_type)
        label(self.sql_label, _("Query type :"), y=1)
        self.query_type_list = list_box(self.sql_label, vbar=False, hbar=False, x=1, y=1, 
                                        selectmode="single", values=["INSERT", "UPDATE"])
        self.query_type = entry(self.sql_label, "", x=2, y=1, disable=True)
        bind_evt("dclick", self.query_type_list, self.maj_query_type)
        """ Bouton de sauvegarde """
        button(self, _("Save"), self.save_query, x=1)
        self.grab_set()

    def maj_db_type(self,evt):
        for index in self.db_type_list.curselection():
            self.db_type[0].set(self.db_type_list.get(index))

    def maj_query_type(self,evt):
        if self.label_query != None:
            self.label_query.destroy()
        for index in self.query_type_list.curselection():
            self.query_type[0].set(self.query_type_list.get(index))
            if self.query_type_list.get(index) == 'INSERT':
                self.display_query('INSERT')
            else:
                self.display_query('UPDATE')

    def save_query(self):
        if self.query_type[0].get() == "UPDATE" and (len(self.set_fields) == 0 or len(self.where_fields) ==0):
            msg(_("Warning"), _("Set or Where list cannot be empty"), type="warning")
        else:     
            options = {}
            options['filetypes'] = [
                (_("SQL files"), ("*.sql")),
                (_("All Files"), "*")]
            options['initialfile'] = 'query_result.sql'
            filename = tkinter.filedialog.asksaveasfilename(**options)
            self.query.sql_export(filename, output_table=self.table_name[0].get(), result_tab=self.query.query_result, 
                                field_names=self.query.query_fields, db_type=self.db_type[0].get(), 
                                query_type=self.query_type[0].get(), set_fields=self.set_fields,
                                where_fields=self.where_fields)
            self.destroy()
    
    def display_query(self, type):
        self.label_query = label_frame(self.sql_label, "{}".format(type)+ _("query") , x=3)
        if type == "INSERT":
            label(self.label_query, "{} INTO ".format(self.query_type[0].get()))
            self.table_name = entry(self.label_query, "", title_value=_("TABLE"), y=1)
        else:            
            label(self.label_query, "{} ".format(self.query_type[0].get()))
            self.table_name = entry(self.label_query, "", title_value=_("TABLE"), y=1)
            label(self.label_query, _("SET"), x=1)
            self.set_fields_list = list_box(self.label_query, vbar=True, hbar=True, x=1, y=1, selectmode="single")
            label(self.label_query, _("WHERE"), x=1, y=3)
            self.where_fields_list = list_box(self.label_query, vbar=True, hbar=True, x=1, y=4, selectmode="single")
            for i in range(0, len(self.query.query_fields)):
                self.set_fields_list.insert(i, self.query.query_fields[i].field_name)
                self.set_fields.append(self.query.query_fields[i])
            bind_evt("dclick", self.set_fields_list, self.maj_where_list)
            bind_evt("dclick", self.where_fields_list, self.maj_set_list)

    def maj_where_list(self, evt):
        for index in self.set_fields_list.curselection():
            self.where_fields_list.insert(self.where_fields_list.size(), self.set_fields[index].field_name)
            self.where_fields.append(self.set_fields[index])
            self.set_fields_list.delete(index, index)
            del self.set_fields[index]
            
    def maj_set_list(self, evt):
        for index in self.where_fields_list.curselection():
            self.set_fields_list.insert(self.set_fields_list.size(), self.where_fields[index].field_name)
            self.set_fields.append(self.where_fields[index])
            self.where_fields_list.delete(index, index)
            del self.where_fields[index]