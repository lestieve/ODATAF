from tkinter import *
from tkinter.ttk import Progressbar, Scrollbar, Treeview
from threading import Thread
from app_tools import *
from app_result import *
from app_dictionary import _, load_dictionary

class AppLog(Toplevel):
    """Window displaying the log if self.display_log of federation is setted to True.
    
    Arguments:
        Toplevel {Toplevel (tkinter)} -- Window preventing actions on other windows
    """
    def __init__(self, federation=None, label=""):
        """Constructor of the AppLog class
        
        Keyword Arguments:
            federation {Federation} -- opened data federation (default: {None})
            label {str} -- name to set for the log window (default: {""})
        """
        Toplevel. __init__(self)
        self.federation = federation
        self.position = 1
        self.title("LOG - {}".format(label))
        self.label_message = label_frame(self, _("Query running..."), x=1, y=0)
        self.progress = Progressbar(self.label_message, orient=HORIZONTAL,length=100,  mode='determinate')
        self.progress.grid(row=0,column=0)
        self.pcent = 0
        self.task_number = 0

        """ Displaying the list of tasks in the log window """
        scrollable_canvas = ScrollableCanvas(self.label_message, width=800, height=350)
        scrollable_canvas.grid(row=2,column=0)
        lib_columns = ["N°", _("Function"), "%", _("Task")]
        nb_cols = len(lib_columns)
        #nb_rows = len(result_tab) 
        cols = [i for i in range(0, nb_cols)]
        scrolly = Scrollbar(scrollable_canvas, orient="vertical")
        scrolly.grid(row=0, column=1, sticky='ns')
        self.tree = Treeview(scrollable_canvas.interior, columns = cols, height = 15, show = "headings")
        self.tree.configure(yscrollcommand=scrolly.set)
        scrolly.config(command=self.tree.yview)
        self.tree.grid(row=0, column=0)
        for i in range(0, nb_cols):
            if i == 0 or i == 2:
                width_column = 30
            elif i == 1:
                width_column = 300
            else:
                width_column = 1000
            self.tree.heading(i, text=lib_columns[i])
            self.tree.column(i, width = width_column)
        self.grab_set()

    def add_log(self, message, progress=0, function=None, close=False):
        """Add a line in the list of tasks
        
        Arguments:
            message {str} -- label of the current task to display
        
        Keyword Arguments:
            progress {int} -- additional percentage to advance the progress bar (default: {0})
            function {str} -- name of the running function (default: {None})
            close {bool} -- if True then display the "CLOSE" button (default: {False})
        """
        self.task_number += 1
        print("{} => {}".format(function, message))
        if progress > 0:
            self.add_progress(value=progress)
        self.tree.insert('', 'end', values = (self.task_number, function, self.pcent, "\"{}\"".format(message)))
        if close == True:
            button(self, _("CLOSE"), self.destroy)

    def add_progress(self, value=0):
        """Advance the progress bar by adding the value
        
        Keyword Arguments:
            value {int} -- value of progress (default: {0})
        """
        if self.pcent + value < 100:
            self.progress.step(value)
            self.pcent += value
        else:
            self.progress.step(99 - self.pcent)
            self.pcent = 100



    