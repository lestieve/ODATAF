import threading
from tkinter import *
import tkinter.filedialog
from odf_query import *
from app_result import *
from app_join import *
from app_filter import *
from app_tools import *
from app_log import *
from app_field import *
from app_to_sql import *
from app_dictionary import _, load_dictionary


class AppQuery(LabelFrame):
    """Frame used to manage the queries of the data federation (saved queries and new query)
    
    Arguments:
        LabelFrame {LabelFrame (tkinter)} -- label frame
    """
    def __init__(self, parent=None, federation=None, app_federation=None, x=1, y=1, display_log=True, app_main=None):
        """Constructor of AppQuery class
        
        Keyword Arguments:
            parent {Frame (tkinter)} -- parent frame (default: {None})
            federation {Federation} -- data federation used for queries (default: {None})
            app_federation {[type]} -- Federation frame instance (default: {None})
            x {int} -- x positioning relative to the parent frame (default: {1})
            y {int} -- y positioning relative to the parent frame (default: {1})
            display_log {bool} -- to display log when a query is executing (default: {True})
            app_main {Tk (tkinter)} -- root window of the app (default: {None})
        """
        LabelFrame.__init__(self, parent, text="", padx=5, pady=0)
        self.window = parent
        self.federation = federation
        self.app_federation = app_federation
        self.display_log = display_log
        self.app_main = app_main
        self.query_fields_app = []
        self.query_joins = []
        self.query_filters = []
        self.grid(row=x,column=y)
        self.log = None
        """ Queries """
        self.queries_name = []
        for query in self.federation.queries:
            self.queries_name.append(query.name)
        frame = Frame(self)
        frame.grid(row=0, column=0)
        queries_label = label_frame(frame, _("Queries"))
        self.queries_list = list_box(queries_label, vbar=True, hbar=True, height=5, width=42, values=self.queries_name)
        bind_evt("click", self.queries_list, self.maj_query)
        button(queries_label, "-", self.del_query, x=0, y=2)
        """ Data results """
        results_label = label_frame(frame, _("Data results"), y=1)
        self.results_list = list_box(results_label, vbar=True, hbar=True, height=5, width=42, values=self.federation.queries_results)
        frame_buttons = Frame(results_label)
        frame_buttons.grid(row=0, column=2)
        button(frame_buttons, ">>", self.display_query_result, x=0)
        bind_evt("dclick", self.results_list, self.display_query_result)
        button(frame_buttons, "-", self.del_result, x=1)
        """ Query frame """
        label_query = label_frame(self, _("Query"), x=1, y=0)
        self.name_entry = entry(label_query, "")
        button(label_query, _("Add query to list"), self.add_query, y=1)
        button(label_query, "X", self.erase_query, x=0, y=2)
        label_query_fields = label_frame(label_query, _("Fields"), x=1, y=0)
        button(label_query_fields, "X", self.del_fields, x=0, y=1)
        self.query_fields_list = list_box(label_query_fields, vbar=True, hbar=True, x=1, y=0, height=8, width=40)
        bind_evt("dclick", self.query_fields_list, self.maj_query_field)
        button(label_query_fields, "-", self.maj_query_fields_del, x=1, y=2)
        self.radio_agregation = radio_button(label_query_fields, [_("Agregate rows"), _("All rows")], text_label=_("Display..."), x=3)
        """ Filters list """
        label_filters = label_frame(label_query, _("Filters"), x=2, y=0)
        button(label_filters, "X", self.del_filters, y=1)
        self.filters_list = list_box(label_filters, vbar=True, hbar=True, x=1, y=0, height=5, width=40)
        bind_evt("dclick", self.filters_list, self.modify_filter)
        frame_filters = Frame(label_filters)
        frame_filters.grid(row=1, column=1)
        button(frame_filters, "+", self.add_filter, x=0, y=0)
        button(frame_filters, "-", self.delete_filter, x=1, y=0)
        """ Joins list """
        label_joins = label_frame(label_query, _("Joins"), x=2, y=1)
        button(label_joins, "X", self.del_joins, x=0, y=1)
        self.joins_list = list_box(label_joins, vbar=True, hbar=True, x=1, y=0, height=5, width=40)
        frame_joins = Frame(label_joins)
        frame_joins.grid(row=1, column=1)
        button(frame_joins, "+", self.add_join, x=0, y=0)
        bind_evt("dclick", self.joins_list, self.modify_join)
        button(frame_joins, "-", self.delete_join, x=1, y=0)
        """ Display options """
        label_display = label_frame(label_query, _("Restitution"), x=1, y=1)
        """ Launch button """
        button(label_display, _("See SQL"), self.see_sql, x=0, y=0)
        button(label_display, _("LAUNCH QUERY"), self.log_start, x=0, y=1)
        self.chk_reload = check_button(label_display, _("Reload tables"), x=1, y=0)
        self.chk_save = check_button(label_display, _("Save data results"), x=1, y=1)
        self.chk_save[1].select()
        label(label_display, _("LIMIT :"), x=2)
        self.limit_list = list_box(label_display, vbar=True, x=2, y=1,
                values=[_("No limit"), 1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 1000, 10000])
        self.limit_list.selection_set(0)
        self.chk_display = check_button(label_display, _("Display"), x=3, y=0)
        self.chk_display[1].select()
        self.chk_excel = check_button(label_display, _("Excel export"), x=3, y=1)
        self.chk_csv = check_button(label_display, _("CSV export"), x=4, y=1)
        self.chk_sql = check_button(label_display, _("SQL query"), x=4, y=0)
    
    def erase_query(self):
        """Resets the query
        """
        self.name_entry[0].set("")
        self.query_fields_list.delete(0,self.query_fields_list.size())
        self.filters_list.delete(0,self.filters_list.size())
        self.joins_list.delete(0,self.joins_list.size())
        self.query_fields_app = []
        self.query_joins = []
        self.query_filters = []

    def del_query(self):
        """Removes the selected query from the queries list and queries of the data federation
        """
        for index in self.queries_list.curselection():
            self.queries_list.delete(index,index)
            del self.federation.queries[index]

    def del_result(self):
        """Removes the selected data results from the data results list
        """
        for index in self.results_list.curselection():
            self.results_list.delete(index,index)
            del self.federation.queries_results[index]

    def del_fields(self):
        """Resets the query fields list
        """
        for i in range(self.query_fields_list.size()):
            self.query_fields_list.delete(0,0)
        self.query_fields_app = []

    def del_filters(self):
        """Resets the query filters list
        """
        for i in range(self.filters_list.size()):
            self.filters_list.delete(0,0)
        self.query_filters = []

    def del_joins(self):
        """Resets the query joins list
        """
        for i in range(self.joins_list.size()):
            self.joins_list.delete(0,0)
        self.query_joins = []

    def maj_query_field(self, evt):
        """Displays the query field edit window
        
        Arguments:
            evt {Event} -- event
        """
        for index in self.query_fields_list.curselection():
            maj_query_field = AppField(self.query_fields_app[index], app_parent=self, query_field_index=index)

    def log_start(self):
        """If display_log is True then creates a new log window
        else launches the query
        """
        if len(self.query_fields_app) > 0:
            self.app_main.save_count(1)
            if self.display_log == True:
                self.query_launched = False
                self.query_finished = False
                self.result = False
                if self.name_entry[0].get() != "":
                    label = self.name_entry[0].get()
                else:
                    label = _("Query n°{}").format(Query.queries_number + 1)
                self.log = AppLog(self.federation, label=label)
                self.log_update()
            else:
                self.launch_query()
                self.display_result(self.query)
        else:
            msg(_("Warning"), _("Select at least one field"), type="warning")

    def log_update(self):
        """When the query is running, creates a new thread and update the log window
        """
        if self.query_finished == True:
            if self.result == True:
                self.log.label_message.configure(text=_("Query terminated"))
                self.display_result(self.query)
            else:
                self.log.label_message.configure(text=_("Query stopped"))
        else:
            if self.query_launched == False:
                self.thread = Thread(target=self.launch_query)
                self.thread.start()
            self.after(100, self.log_update)

    def launch_query(self):
        """Launches a new query
        """
        self.query_launched = True
        self.query = self.build_query()
        self.result = self.query.execute()
        if self.result == True:
            log(self.log, _("## Displaying results..."), progress=20, function="AppQuery.launch_query", close=True)
        else:
            log(self.log, _("## Query stopped due to an error"), progress=20, function="AppQuery.launch_query", close=True)
        self.app_main.save_count(0)
        self.query_finished = True
        
    def display_result(self, query):
        """Displays the data results in a new window or exports it in the selected format
        
        Arguments:
            query {Query} -- query to display
        """
        if self.chk_save[0].get() == 1:
            self.federation.queries_results.append([query.query_name, query.query_result, query.field_labels()])
            self.results_list.insert(self.results_list.size(), query.query_name)
        if self.chk_display[0].get() == 1:
            table_result = ResultDisplay(query.query_name, query.query_result, self.query.field_labels())
        if self.chk_excel[0].get() == 1:
            options = {}
            options['filetypes'] = [
                (_("Excel files"), ("*.xls", "*.xlsx", "*.xlsm")),
                (_("All Files"), "*")]
            options['initialfile'] = 'query_result.xlsx'
            filename = tkinter.filedialog.asksaveasfilename(**options)
            excel_export(filename, result_tab=query.query_result, field_names=self.query.field_labels())
        if self.chk_csv[0].get() == 1:
            options = {}
            options['filetypes'] = [
                (_("CSV files"), ("*.csv")),
                (_("All Files"), "*")]
            options['initialfile'] = 'query_result.csv'
            filename = tkinter.filedialog.asksaveasfilename(**options)
            csv_export(filename, result_tab=query.query_result, field_names=self.query.field_labels())
        if self.chk_sql[0].get() == 1:
            new_query = AppToSql(query, app_parent=self)

    def display_query_result(self, evt=None):
        """Displays the selected data results in the data results list
        
        Keyword Arguments:
            evt {Event} -- event (default: {None})
        """
        for index in self.results_list.curselection():
            table_result = ResultDisplay(self.federation.queries_results[index][0],
                                        self.federation.queries_results[index][1], 
                                        self.federation.queries_results[index][2])

    def build_query(self):
        """Builds the query before executing it
        """
        if self.radio_agregation[0].get() == 0:
            agreg = True
        else:
            agreg = False
        limit = None
        for index in self.limit_list.curselection():
            if self.limit_list.get(index) == _("No limit"):
                limit = None
            else:
                limit = int(self.limit_list.get(index))
        if self.chk_reload[0].get() == 1:
            reload = True
        else:
            reload = False
        return Query(self.federation, self.query_fields_app, self.query_joins, 
                                self.query_filters, log=self.log, agregate=agreg, limit=limit, 
                                reload=reload, query_name=self.name_entry[0].get())
        
    def add_query(self):
        """Adds the query into the queries list of the data federation
        """
        query = self.build_query()
        exists = False
        for qry in self.federation.queries:
            if qry.query_name == query.query_name:
                exists = True
        if exists:
            msg(_("Warning"), _("Query name already exists"), type="warning")
        else:
            self.queries_list.insert(self.queries_list.size(), str(query.query_name))
            self.federation.add_query(query)

    def maj_query_fields_del(self):
        """Removes the selected query field in the query fields list
        """
        try:
            for index in self.query_fields_list.curselection():
                del self.query_fields_app[index]
            self.query_fields_list.delete(index,index)
        except:
            pass

    def add_filter(self):
        """Opens the window for creating a new filter
        """
        if len(self.federation.sources) > 0:
            tables_app = []
            for field in self.query_fields_app:
                tables_app.append(field.table)
            tables_app = list(dict().fromkeys(tables_app).keys())
            new_filter = AppFilter(federation=self.federation, app_parent=self, 
                                    query_filters=self.query_filters, query_tables=tables_app)

    def delete_filter(self):
        """Removes the selected query filter in the query filters list
        """
        for index in self.filters_list.curselection():
            del self.query_filters[index]           
            self.filters_list.delete(index, index)

    def modify_filter(self,evt):
        """Opens the query filter edit window
        
        Arguments:
            evt {Event} -- event
        """
        tables_app = []
        for field in self.query_fields_app:
            tables_app.append(field.table)
        #tables_app = list(set(tables_app))
        tables_app = list(dict().fromkeys(tables_app).keys())
        for table in tables_app:
            print(_("table : ") + table.target_name)
        for index in self.filters_list.curselection():
            new_filter = AppFilter(federation=self.federation, app_parent=self, 
                                query_filters=self.query_filters, query_tables=tables_app, filter_index=index)

    def add_join(self): 
        """Opens the window for creating a new join
        """
        if len(self.federation.sources) > 0:
            tables_app = []
            for field in self.query_fields_app:
                tables_app.append(field.table)
            tables_app = list(dict().fromkeys(tables_app).keys())
            new_join = AppJoin(federation=self.federation, app_parent=self, tables_list=tables_app, joins=self.query_joins)

    def delete_join(self):
        """Removes the selected query join in the query joins list
        """
        for index in self.joins_list.curselection():
            del self.query_joins[index]           
            self.joins_list.delete(index, index)

    def modify_join(self,evt):
        """[summary]
        
        Arguments:
            evt {[type]} -- [description]
        """
        tables_app = []
        for field in self.query_fields_app:
            tables_app.append(field.table)
        #tables_app = list(set(tables_app))
        tables_app = list(dict().fromkeys(tables_app).keys())
        for table in tables_app:
            print(_("table : ") + table.target_name)
        for index in self.joins_list.curselection():
            new_join = AppJoin(federation=self.federation, app_parent=self, tables_list=tables_app, joins=self.query_joins, join_index=index)

    def maj_query(self, evt):
        """Opens the edit window for the selected query join in the query joins list
        
        Arguments:
            evt {Event} -- event
        """
        query = None
        query_name = ""
        for index in self.queries_list.curselection():
            query = self.federation.queries[index]
            query_name = self.federation.queries[index].query_name
        # Delete query
        self.del_fields()
        self.del_filters()
        self.del_joins()
        self.query_fields_app = []
        self.query_joins = []
        self.query_filters = []
        # Query name
        self.name_entry[0].set(query_name)
        # Fields
        try:
            for i in range(0, len(query.query_fields)):
                self.query_fields_list.insert(i, query.query_fields[i].field_label())
                self.query_fields_app.append(query.query_fields[i])
        except:
            pass
        # Filters
        try:
            for i in range(0, len(query.query_filters)):
                self.filters_list.insert(i, query.query_filters[i].description)
                self.query_filters.append(query.query_filters[i])
        except:
            pass
        # joins
        try:
            for i in range(0, len(query.query_joins)):
                self.joins_list.insert(i, query.query_joins[i].name)
                self.query_joins.append(query.query_joins[i])
        except:
            pass

    def see_sql(self):
        """Displays the SQL query
        """
        if len(self.query_fields_app) > 0:
            self.log = None
            query = self.build_query()
            query.list_sources_tables()
            sql = query.sql_generation()
            display_sql = AppSQL(sql)
        else:
            msg(_("Warning"), _("Select at least one field"), type="warning")


class AppSQL(Toplevel):
    """SQL query display window
    
    Arguments:
        Toplevel {Toplevel (tkinter)} -- Window preventing actions on other windows
    """
    def __init__(self, sql):
        """Constructor of the AppSQL class
        
        Arguments:
            sql {str} -- SQL query
        """
        Toplevel.__init__(self)
        self.sql = sql
        SQL_label = label_frame(self, _("SQL query"), x=0, y=0)
        text(SQL_label, self.sql, height=20, width=100)
        button(self, "OK", self.destroy, x=1)






    