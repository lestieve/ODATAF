from tkinter import *
from tkinter.messagebox import *
from itertools import count
import pickle
from odf_federation import *
from app_tool_bar import *
from app_federation import *
from app_query import *
from app_tools import *
from app_dictionary import _, load_dictionary

class App(Tk):
    """Root window of the application
    
    Arguments:
        Tk {Tk (tkinter)} -- Tk window
    """
    def __init__(self):
        """Constructor of the App class
        """
        self.load_settings()
        load_dictionary(lang=self.lang)
        self.save_path = "cache_file"
        self.version = "1.43.1"
        self.count()
        if self.count_obj == 0:
            Tk.__init__(self)
            self.display_log = True
            self.federation = Federation(_("New data federation"))
            self.change_title(self.federation.name)
            self.global_frame = Frame(self)
            self.global_frame.grid(row=1, column=0)
            self.app_query = AppQuery(parent=self.global_frame, federation= self.federation, 
                                        x=0, y=1, display_log=self.display_log, app_main=self)
            self.app_federation = AppFederation(parent=self.global_frame, federation= self.federation, x=0, y=0, app_query=self.app_query, app_main=self)
            tool_bar_frame = Frame(self)
            tool_bar_frame.grid(row=0, column=0)
            self.app_tool_bar = AppToolBar(parent=tool_bar_frame, app_main=self, app_federation=self.app_federation, x=0, y=0) 
            canvas = Canvas(tool_bar_frame, width=600, height=10)  
            canvas.grid(row=0, column=1)
            self.menu_bar()
            self.mainloop()

    def count(self):
        """Counts the number of opened windows by incrementing the counter present in the file cache_file. 
            This is to prevent multiple windows from opening because of multiprocessing
        """
        try:
            with open(self.save_path, 'rb') as file:
                my_depickler = pickle.Unpickler(file)
                self.count_obj = my_depickler.load()
        except:
            self.count_obj = 0
            
    def save_count(self, number):
        """Saves the counter in cache_file
        
        Arguments:
            number {int} -- counter
        """
        try:
            with open(self.save_path, 'wb') as file:
                my_pickler = pickle.Pickler(file)
                self.count_obj = number
                my_pickler.dump(self.count_obj)
        except:
            pass

    def change_title(self, title):
        """Changes the title of the window root app
        
        Arguments:
            title {str} -- title to set
        """
        self.title("Open DATA Federator - {}".format(title))
    
    def menu_bar(self):
        """Shows and manage menu bar
        """
        def alert():
            msg("About", "Version : ODATAF {}".format(self.version), type="info", command_true=None, command_false=None)
        def add_mysql():
            self.app_federation.add_db_source(type="MYSQL")
        def add_postgres():
            self.app_federation.add_db_source(type="POSTGRES")
        def add_excel():
            self.app_federation.add_file_source(type="EXCEL")
        def add_csv():
            self.app_federation.add_file_source(type="CSV")
        def add_json():
            self.app_federation.add_file_source(type="JSON")
        def add_xml():
            self.app_federation.add_file_source(type="XML")

        menubar = Menu(self)

        menu1 = Menu(menubar, tearoff=0)
        menu1.add_command(label=_("New data federation"), command=self.app_federation.new_federation)
        menu1.add_command(label=_("Open data federation without queries"), command=self.app_federation.restore_federation_app)
        menu1.add_command(label=_("Open data federation and queries"), command=self.app_federation.restore_fed_and_queries)
        menu1.add_command(label=_("Save as"), command=self.save_federation_as)
        menu1.add_separator()
        menu1.add_command(label=_("Settings"), command=self.settings)
        menu1.add_separator()
        menu1.add_command(label=_("Exit"), command=self.destroy)
        menubar.add_cascade(label=_("Data Federation"), menu=menu1)

        menu2 = Menu(menubar, tearoff=0)
        menu2.add_command(label="MySQL", command=add_mysql)
        menu2.add_command(label="PostgreSQL", command=add_postgres)
        menu2.add_command(label="SQLite", command=self.app_federation.add_sqlite_source)
        menu2.add_command(label="Excel", command=add_excel)
        menu2.add_command(label="CSV", command=add_csv)
        menu2.add_command(label="JSON", command=add_json)
        menu2.add_command(label=_("Rest API"), command=add_json)
        menu2.add_command(label="XML", command=add_xml)
        menubar.add_cascade(label=_("Insert source"), menu=menu2)

        menu3 = Menu(menubar, tearoff=0)
        menu3.add_command(label=_("About"), command=alert)
        menubar.add_cascade(label=_("Help"), menu=menu3)

        self.config(menu=menubar)

    def save_federation_as(self):
        """Opens the Save As dialog box
        """
        self.app_federation.save_federation_name(save_as=True)


    def save_settings(self, binary_path="settings.dat"):
        """Saves the settings in the settings.dat file
        
        Keyword Arguments:
            binary_path {str} -- path to the binary file to save (default: {"settings.dat"})
        """
        with open(binary_path, 'wb') as file:
            my_pickler = pickle.Pickler(file)
            my_pickler.dump(self.lang)

    def load_settings(self, binary_path="settings.dat"):
        """Loads the settings from a binary file
        
        Keyword Arguments:
            binary_path {str} -- path to the binary file to load (default: {"settings.dat"})
        """
        try:
            with open(binary_path, 'rb') as file:
                my_depickler = pickle.Unpickler(file)
                self.lang = my_depickler.load()
                print("language : {}".format(self.lang))
        except:
            self.lang = "en"
            print("language : {}".format(self.lang))
    
    def settings(self):
        """Displays the settings window
        """
        settings = AppSettings(self)