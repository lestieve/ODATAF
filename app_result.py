from tkinter import *
from tkinter import ttk
import tkinter.filedialog
from odf_tools import *
from app_dictionary import _, load_dictionary


class ScrollableCanvas(Frame):
    def __init__(self, parent, bg='#FFFFFF', width=1000, height=600, scrollregion=(0,0,500,500)):
        Frame.__init__(self, parent)
        canvas=Canvas(self, bg=bg, width=width, height=height, scrollregion=scrollregion)

        vbar=Scrollbar(self,orient='vertical')
        vbar.grid(row=0, column=1, sticky='ns')
        vbar.config(command=canvas.yview)

        hbar=Scrollbar(self,orient='horizontal')
        hbar.grid(row=1, column=0, sticky='ew')
        hbar.config(command=canvas.xview)

        canvas.config(yscrollcommand=vbar.set)
        canvas.config(xscrollcommand=hbar.set)
        canvas.grid(row=0, column=0, sticky='nsew')
        
        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=NW )

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            """if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())"""
        canvas.bind('<Configure>', _configure_canvas)

class ResultDisplay(Tk):

    def __init__(self, query_name, result_tab, field_labels, width_coef=8):
        Tk.__init__(self)
        self.result_tab = result_tab
        self.field_labels = field_labels
        self.title(_("DATA RESULTS") + " - {}".format(query_name))
        # width_column identification
        nb_cols = len(field_labels)
        nb_rows = len(result_tab)
        max = [10 for i in range(0, nb_cols)]
        for i in range(0, nb_rows):
            for j in range(0, nb_cols):
                try:
                    if isinstance(result_tab[i][j], int):
                        max[j] = 10
                    elif result_tab[i][j] is None:
                        max[j] = 10
                    else:
                        if len(result_tab[i][j]) > max[j]:
                            max[j] = len(result_tab[i][j])    
                except TypeError:
                    max[j] = 10

        sum = 0
        for j in range(0, nb_cols):
            sum += max[j]
        if sum * width_coef >= 1000:
            window_width = 1000
        else:
            window_width = sum * width_coef
        frame_buttons = Frame(self)
        frame_buttons.grid(row=0, column=0)
        Button(frame_buttons, text="EXCEL", command=self.excel_export_app).grid(row=0, column=0)
        Button(frame_buttons, text="CSV", command=self.csv_export_app).grid(row=0, column=1)
        Button(frame_buttons, text="JSON", command=self.json_export_app).grid(row=0, column=2)
        Button(frame_buttons, text="X", command=self.close_window).grid(row=0, column=3)
        frame = Frame(self)
        frame.grid(row=1, column=0)
        scrollable_canvas = ScrollableCanvas(frame, width=window_width)
        scrollable_canvas.grid(row=1,column=0)
        """lib_columns = []
        for field in fields_name:
            if field.alias == "":
                lib_columns.append(field.field_name)
            else:
                lib_columns.append(field.alias)"""
        
        cols = [i for i in range(0, nb_cols)]

        scrolly = ttk.Scrollbar(scrollable_canvas, orient="vertical")
        
        scrolly.grid(row=0, column=1, sticky='ns')
        
        tree = ttk.Treeview(scrollable_canvas.interior, columns = cols, height = 29, show = "headings")
        
        tree.configure(yscrollcommand=scrolly.set)
        scrolly.config(command=tree.yview)
        
        tree.grid(row=0, column=0)

        for i in range(0, nb_cols):
            tree.heading(i, text=field_labels[i])
            tree.column(i, width = max[i]*width_coef)

        for j in range(0, nb_cols):
            print("col{} => {}".format(j, max[j]))

        for row in result_tab:
            tree.insert('', 'end', values = row )

        self.mainloop()   

    def close_window(self):
        self.destroy()

    def excel_export_app(self):      
        options = {}
        options['filetypes'] = [
            (_("Excel files"), ("*.xls", "*.xlsx", "*.xlsm")),
            (_("All Files"), "*")]
        options['initialfile'] = 'query_result.xlsx'
        filename = tkinter.filedialog.asksaveasfilename(**options)
        excel_export(filename, result_tab=self.result_tab, field_names=self.field_labels)    

    def csv_export_app(self):   
        options = {}
        options['filetypes'] = [
            (_("CSV files"), ("*.csv")),
            (_("All Files"), "*")]
        options['initialfile'] = 'query_result.csv'
        filename = tkinter.filedialog.asksaveasfilename(**options)
        csv_export(filename, result_tab=self.result_tab, field_names=self.field_labels)

    def json_export_app(self):   
        options = {}
        options['filetypes'] = [
            (_("JSON files"), ("*.json")),
            (_("All Files"), "*")]
        options['initialfile'] = 'query_result.json'
        filename = tkinter.filedialog.asksaveasfilename(**options)
        json_export(filename, result_tab=self.result_tab, field_names=self.field_labels)