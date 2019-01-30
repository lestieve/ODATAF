from tkinter import *
import tkinter.filedialog
import os
from odf_federation import *
from odf_source import *
from app_join import *
from app_tools import *
from app_result import *
from app_selector import *
from app_query import *
from app_dictionary import _, load_dictionary 

class AppFederation(LabelFrame):
    """Class of the AppFederation object, a LabelFrame object who contains the widgets
    used to manage a federation (sources, tables, fields and joins)
    """
    def __init__(self, parent=None, federation=None, x=1, y=0, app_query=None, app_main=None):
        """Constructor of the AppFederation object
        
        Arguments:
            LabelFrame {LabelFrame} -- principal LabelFrame
        
        Keyword Arguments:
            parent {Frame} -- parent frame (default: {None})
            federation {Federation} -- used data federation (default: {None})
            x {int} -- x coordinate (default: {1})
            y {int} -- y coordinate (default: {0})
            app_query {AppQuery} -- query frame (default: {None})
            app_main {AppMain} -- root frame (default: {None})
        """
        LabelFrame.__init__(self, parent, text=_("Data federation"),padx=5, pady=0)
        self.grid(row=x, column=y)
        self.app_main = app_main
        self.app_query = app_query
        self.federation = federation
        """ Sources, tables and fields selector"""
        self.app_sel = AppSelector(self, federation=self.federation, app_federation=self, app_query=self.app_query, 
                                    modify_source=True, select_button="=>", refresh=True)
        """Permanent joins"""
        label_joins = label_frame(self, _("Joins"), x=2, y=0)
        self.joins_list = list_box(label_joins, vbar=True, hbar=True, x=0, y=0, width=40, height=8)
        frame = Frame(label_joins)
        frame.grid(row=0, column=2)
        button(frame, "+", self.add_join, x=0, y=0)
        bind_evt("dclick", self.joins_list, self.modify_join)
        button(frame, "-", self.delete_join, x=1, y=0)

    def add_file_source(self, type, source_index=None):
        """Opens a new window used to add a new file source.
        
        Arguments:
            type {str} -- name of the file type (EXCEL, CSV, JSON,...)
        
        Keyword Arguments:
            source_index {int} -- index of the selected source to update (default: {None})
        """
        self.source_index = source_index
        self.source_type = type
        if type == "EXCEL":
            self.filetypes = [
                ("Excel files", ("*.xls", "*.xlsx", "*.xlsm")),
                ("All Files", "*")]
        if type == "CSV":
            self.filetypes = [
                    ("CSV files", ("*.csv")),
                    ("All Files", "*")]
        if type == "JSON":
            self.filetypes = [
                    ("JSON files", ("*.json")),
                    ("All Files", "*")]
        # id source determination
        i = 0
        for source in self.federation.sources:
            if source.type == self.source_type:
                i += 1
        self.id_source = i + 1
        # Display the new window 
        self.second_window = tkinter.Toplevel()
        self.source_name = entry(self.second_window, _("Source name"), x=0, y=0)
        if type == "API":
            self.url = entry(self.second_window, "URL", x=1, y=0, width_entry=50)
        # Source modification
        if source_index != None:
            self.source_name[0].set(self.federation.sources[source_index].name)
            if type == "API":
                self.url[0].set(self.federation.sources[source_index].file_path)
            else:
                label(self.second_window, _("File path :"), x=1, y=0)
                label(self.second_window, self.federation.sources[source_index].file_path, x=1, y=1)
            button(self.second_window, _("Update source"), self.update_file_source, x=2, y=1)
            button(self.second_window, _("Delete source"), self.delete_source, x=3, y=1)
        else:
            self.source_name[0].set(type + _(" source ") + str(self.id_source))
            if type == "API":
                button(self.second_window, _("Save source"), self.save_file_source, x=2, y=1)
            else:
                button(self.second_window, _("Select file to import"), self.save_file_source, x=1, y=1)
        self.second_window.grab_set() 

    def save_file_source(self):
        """After giving the characteristics of the file, open the dialog box
         to select the file.
        """
        if self.source_type == "API":
            filename = self.url[0].get()
            table_name = "json{}".format(self.id_source)
        else:
            """ Ouverture de la boite de dialogue """
            filename = self.open_file(filetypes=self.filetypes)
            if self.source_type == "JSON":
                table_name = "json{}".format(self.id_source)
            else:
                table_name = ""
        source = FileSource(self.federation, id = self.id_source, type = self.source_type, 
                    name = self.source_name[0].get(), file_path = filename, table_name=table_name)
        print("source:" + str(self.source_name[0].get()))
        print("file:" + str(filename))
        self.federation.add_source(source)
        self.federation.list_sources_tables_fields()
        self.app_sel.sources_list.insert(len(self.federation.sources),source.name)
        self.second_window.destroy()

    def open_file(self, filetypes=None):
        """Opens the file selection dialog
        
        Keyword Arguments:
            filetypes {list} -- list containing the setting 
                                of the file type to select (default: {None})
        """
        """filetypes = [
                ("HTML Files", "*.htm *.html", "TEXT"),
                ("PDF Files", "*.pdf", "TEXT"),
                ("Windows Help Files", "*.chm"),
                ("Text Files", "*.txt", "TEXT"),
                ("All Files", "*")]"""
        base = None
        if filetypes == None:
            filetypes = self.filetypes
        opendialog = tkinter.filedialog.Open(parent=self, filetypes=filetypes)
        filename = opendialog.show(initialdir=dir, initialfile=base)
        print("filename => {}".format(filename))
        return filename

    def add_db_source(self, type, source_index=None):
        """Opens the dialog box for defining the characteristics of the database source
        
        Arguments:
            type {str} -- MYSQL, POSTGRES
        
        Keyword Arguments:
            source_index {int} -- selected index in the sources 
                                    list for modification (default: {None})
        """
        self.source_index = source_index
        if type == "MYSQL":
            self.source_type = "MYSQL"
        elif type == "POSTGRES":
            self.source_type = "POSTGRES"
        # Détermination de l'id source
        i = 0
        for source in self.federation.sources:
            if source.type == self.source_type:
                i += 1
        self.id_source = i + 1
        self.second_window = tkinter.Toplevel()
        """ Source name """
        self.source_name = entry(self.second_window, _("Source name"), x=0, y=0)
        """ Host """
        self.host_url = entry(self.second_window, _("Host URL"), x=1, y=0, width_entry=50)
        if type == "POSTGRES":
            self.port = entry(self.second_window, _("Port"), x=1, y=2, width_entry=10)
        """ User """
        self.user_var = entry(self.second_window, _("User"), x=2, y=0)
        """ Password """
        self.password_var = entry(self.second_window, _("Password"), x=3, y=0, show="*")
        """ Database """
        self.database_var = entry(self.second_window, _("Database"), x=4, y=0)
        """ Add or source modification """
        if source_index != None:
            self.source_name[0].set(self.federation.sources[source_index].name)
            self.host_url[0].set(self.federation.sources[source_index].host)
            if type == "POSTGRES":
                self.port[0].set(self.federation.sources[source_index].port)
            self.user_var[0].set(self.federation.sources[source_index].user)
            self.password_var[0].set(self.federation.sources[source_index].password)
            self.database_var[0].set(self.federation.sources[source_index].database)
            button(self.second_window, _("Update database source"), self.update_db_source, x=5, y=2)
            button(self.second_window, _("Delete database source"), self.delete_source, x=6, y=2)
        else:
            self.source_name[0].set("{} source {}".format(self.source_type, self.id_source))
            self.host_url[0].set("localhost")
            if type == "POSTGRES":
                self.port[0].set("5432")
            button(self.second_window, _("Save database source"), self.save_db_source, x=5, y=2)
        self.second_window.grab_set()      

    def add_sqlite_source(self, source_index=None):
        """Opens the dialog box for defining the characteristics of a SQLITE source
        
        Keyword Arguments:
            source_index {int} -- selected index in the sources 
                                    list for modification (default: {None})
        """
        self.source_index = source_index
        # Détermination de l'id source
        
        self.second_window = tkinter.Toplevel()
        if source_index == None:
            i = 0
            for source in self.federation.sources:
                if source.type == "SQLITE":
                    i += 1
            self.id_source = i + 1
            source_name = "SQLite source " + str(self.id_source)
        else:
            source_name = self.federation.sources[source_index].name
        self.source_name = entry(self.second_window, _("Source name"), x=0, y=0, width_entry=30)
        self.source_name[0].set(source_name)
        if source_index == None:
            open_file = button(self.second_window, _("Select SQLite file"), self.open_sqlite_file, x=1, y=1)
        else:
            label(self.second_window, _("File path : "), x=1, y=0)
            label(self.second_window, self.federation.sources[source_index].file_path, x=1, y=1)
            button(self.second_window, _("Update source"), self.update_file_source, x=2, y=1)
            button(self.second_window, _("Delete source"), self.delete_source, x=3, y=1)
        self.second_window.grab_set() 

    def open_sqlite_file(self):
        """Opens the file selection dialog for a SQLITE source
        """
        filetypes = [
                ("SQLite file", ("*.sqlite")),
                ("All Files", "*")]
        base = None
        opendialog = tkinter.filedialog.Open(parent=self, filetypes=filetypes)
        filename = opendialog.show(initialdir=dir, initialfile=base)
        if os.path.basename(filename) != self.federation.sqlite_path:
            source = DBSource(self.federation, "SQLITE", self.id_source, self.source_name[0].get(), host="",
                            user="", password="", database="", file_path=filename)
            print("source:" + str(self.source_name[0].get()))
            self.federation.add_source(source)
            self.federation.list_sources_tables_fields()
            self.app_sel.sources_list.insert(len(self.federation.sources),source.name)
            self.second_window.destroy()
        else:
            msg(_("Warning"), _("You can't add this SQLite database. Select other one."), type="warning")

    def save_db_source(self):
        """Add the database source in the data federation
        """
        if self.source_type == "POSTGRES":
            port = self.port[0].get()
        else:
            port = ""
        source = DBSource(self.federation, self.source_type, self.id_source, self.source_name[0].get(), host=self.host_url[0].get(),
                            user=self.user_var[0].get(), password=self.password_var[0].get(), database=self.database_var[0].get(), 
                            port=port)
        print("source:" + str(self.source_name[0].get()))
        self.federation.add_source(source)
        self.federation.list_sources_tables_fields()
        self.app_sel.sources_list.insert(len(self.federation.sources),source.name)
        self.second_window.destroy()

    def add_join(self):
        """Open a AppJoin window for add a new join
        """
        if len(self.federation.sources) > 0:
            new_join = AppJoin(federation=self.federation, app_parent=self, tables_list=[], joins=self.federation.joins)
    
    def delete_join(self):
        """Delete the selected join in the joins list from the data federation
        """
        for index in self.joins_list.curselection():
            del self.federation.joins[index]           
            self.joins_list.delete(index, index)

    def modify_join(self,evt):
        """Open the AppJoin window for join modification
        
        Arguments:
            evt {event object} -- event
        """
        for index in self.joins_list.curselection():
            new_join = AppJoin(federation=self.federation, app_parent=self, tables_list=[], joins=self.federation.joins, join_index=index)

    def save_federation_name(self, save_as = False):
        """Opens a dialog box to set the data federation name to save.
        
        Keyword Arguments:
            save_as {bool} -- if true, it will open the dialog box 
                            to select the file to save (default: {False})
        """
        if save_as == True or self.federation.save_path == "":
            # Affichage de la boite de dialogue pour le nom de la federation 
            self.second_window = tkinter.Toplevel()
            self.second_window.title(_("Save as"))
            #this forces all focus on the top level until Toplevel is closed
            self.federation_name = entry(self.second_window, _("Federation name"), title_value=self.federation.name, x=0, y=0, )
            button(self.second_window, _("Select directory"), self.save_federation_app, x=0, y=2)
            self.second_window.grab_set()
        else:
            self.federation.save_queries(self.federation.save_path)
            
    def save_federation_app(self):
        """Opens the file selection dialog and launch the federation save function.
        """
        options = {}
        options['filetypes'] = [('all files', '.*'), ('text files', '.odf')]
        options['initialfile'] = 'myfile.odf'
        filename = tkinter.filedialog.asksaveasfilename(**options)
        self.federation.name = self.federation_name[0].get()
        self.federation.save_queries(filename)
        self.app_main.change_title(self.federation.name) 
        self.second_window.destroy()

    def restore_federation_app(self):
        """Opens a file selection dialog and launch the restore function of a data federation.
        """
        filetypes = [(_("Data federation files"), "*.odf")]
        base = None    
        opendialog = tkinter.filedialog.Open(parent=self, filetypes=filetypes)
        filename = opendialog.show(initialdir=dir, initialfile=base)
        self.new_federation()
        self.federation.restore_federation(filename)
        i = 0
        for source in self.federation.sources:
            self.app_sel.sources_list.insert(i,source.name)
            i += 1
        i = 0
        for join in self.federation.joins:
            self.joins_list.insert(i, join.name)
            i += 1
        self.app_main.change_title(self.federation.name) 
    
    def restore_fed_and_queries(self):
        """Launches the restore function of a data federation including queries and results
        """
        self.restore_federation_app()
        i = 0
        for query in self.federation.queries:
            self.app_query.queries_list.insert(i, query.query_name)
            i += 1
        i = 0
        for result in self.federation.queries_results:
            self.app_query.results_list.insert(i, result[0])
            i += 1
        self.app_main.change_title(self.federation.name) 

    def modify_source(self,evt):
        """Opens the dialog for the type of source for editing
        
        Arguments:
            evt {event object} -- event
        """
        for index in self.app_sel.sources_list.curselection():
            source = self.federation.sources[index]
            if source.general_type == "DB":
                if source.type == "MYSQL":
                    self.add_db_source(source.type, source_index=index)
                elif source.type == "POSTGRES":
                    self.add_db_source(source.type, source_index=index)
                elif source.type == "SQLITE":
                    self.add_sqlite_source(source_index=index)
            elif source.general_type == "FILE":
                self.add_file_source(source.type, source_index=index)

    def update_file_source(self):
        """Launchs the name update function of the selected source
        """
        self.federation.update_source(self.source_index, self.source_name[0].get())
        self.app_sel.sources_list.delete(self.source_index,self.source_index)
        self.app_sel.sources_list.insert(self.source_index,self.source_name[0].get())
        self.second_window.destroy()

    def delete_source(self):
        """Launchs the delete function of the selected source
        """
        i = 0
        for join in self.federation.joins:
            if join.left_source == self.federation.sources[int(self.source_index)].name or \
                join.right_source == self.federation.sources[int(self.source_index)].name:
                self.joins_list.delete(i,i)
            else:
                i += 1
        self.federation.delete_source(self.source_index)
        self.app_sel.sources_list.delete(self.source_index, self.source_index)
        self.app_sel.tables_listbox.delete(0,self.app_sel.tables_listbox.size())
        self.app_sel.fields_list.delete(0,self.app_sel.fields_list.size())
        self.second_window.destroy()
        
    def update_db_source(self):
        """Updates the database source from the settings entered in the edit dialog
        """
        self.federation.sources[self.source_index].name = self.source_name[0].get()
        self.federation.sources[self.source_index].host = self.host_url[0].get()
        self.federation.sources[self.source_index].user = self.user_var[0].get()
        self.federation.sources[self.source_index].password = self.password_var[0].get()
        self.federation.sources[self.source_index].database = self.database_var[0].get()
        self.app_sel.sources_list.delete(self.source_index,self.source_index)
        self.app_sel.sources_list.insert(self.source_index,self.source_name[0].get())
        self.second_window.destroy()

    def new_federation(self):
        """Resets the interface for a new data federation
        """
        self.federation = self.app_main.federation = None
        self.federation = self.app_main.federation = Federation(_("New data federation"))
        self.app_main.change_title(_("New data federation")) 
        self.app_query = None
        self.app_query = AppQuery(parent=self.app_main.global_frame, federation= self.federation, 
                                    x=0, y=1, display_log=self.app_main.display_log, app_main=self.app_main)
        self.app_sel = None
        self.app_sel = AppSelector(self, federation=self.federation, app_federation=self, app_query=self.app_query, modify_source=True,
                                    select_button="=>", refresh=True)
        self.joins_list.delete(0,self.joins_list.size()) 
        try:
            os.remove(self.federation.sqlite_path)
        except:
            pass
        