from tkinter import *
from tkinter.messagebox import *

def label(parent, text_label, x=0, y=0):
    label_tables = Label(parent,text=text_label).grid(row=x, column=y)

def text(parent, text, x=0, y=0, height=2, width=30):
    text_to_display = Text(parent,height=height, width=width)
    text_to_display.insert(END, text)
    text_to_display.grid(row=x, column=y)

def label_frame(parent, text_label, x=0, y=0):
    label_fr = LabelFrame(parent, text=text_label,padx=5, pady=0)
    label_fr.grid(row=x,column=y)
    return label_fr

def list_box(parent, vbar=True, hbar=False, x=0, y=0, width=20, height=2, 
                text_label="", selectmode="single", values=[]):
    local_parent = parent
    x_local = x
    y_local = y
    if text_label != "":
        label_frame = LabelFrame(parent, text=text_label,padx=5, pady=0)
        label_frame.grid(row=x,column=y)
        local_parent = label_frame
        x_local = 0
        y_local = 0
    if vbar == True:
        yDefilB = Scrollbar(local_parent, orient='vertical')
        yDefilB.grid(row=x_local, column=y_local+1, sticky='ns')
    if hbar == True:
        xDefilB = Scrollbar(local_parent, orient='horizontal')
        xDefilB.grid(row=x_local+1, column=y_local, sticky='ew')

    canvas = Listbox(local_parent, selectmode=selectmode, width=width, height=height)
    if vbar == True:
        canvas.config(yscrollcommand=yDefilB.set)
        yDefilB.config(command=canvas.yview)
    if hbar == True:
        canvas.config(xscrollcommand=xDefilB.set)
        xDefilB.config(command=canvas.xview)
    canvas.grid(row=x_local, column=y_local, sticky='nsew')
    if values !=[]:
        i = 0
        for value in values:
            canvas.insert(i, value)
            i += 1
    return canvas

def entry(parent, title, title_value="", x=0, y=0, width_entry=30, show="", disable=False):
    if title != "":
        Label(parent,text=title + " :").grid(row=x,column=y)
    entry_var = StringVar(parent)
    entry = Entry(parent, textvariable=entry_var, width=width_entry)
    if show != "":
        entry.config(show = show)
    if title != "":
        entry.grid(row = x, column = y+1)
    else:
        entry.grid(row = x, column = y)
    entry_var.set(title_value)
    if disable == True:
        entry.config(state='disabled')
    return [entry_var, entry]

def button(parent, title, command_button, x=0, y=0, display=None):
    button=Button(parent, text=title, command=command_button)
    button.grid(row = x, column = y)
    if display != None:
        display[button] = True
    return button 

def show_hide(object, x=0, y=0, action="show"):
    if action == "show":
        object.grid(row=x, column=y)
    elif action == "hide":
        object.grid_forget()
        
def bind_evt(evt, obj, fct):
    if evt == "click":
        obj.bind('<ButtonRelease>', fct)   
        obj.bind('<ButtonPress>',fct) 
        obj.bind('<KeyPress-Up>',fct)    
        obj.bind('<KeyPress-Down>',fct)
    elif evt == "dclick":
        obj.bind('<Double-Button-1>', fct) 

def check_button(parent, text_label, x=0, y=0, width=10, height=1):
    chk_var = IntVar()
    chk = Checkbutton(parent, text = text_label, variable = chk_var,
                 onvalue = 1, offvalue = 0, height=height, width = width)
    chk.grid(row = x, column = y)
    return [chk_var, chk]

def radio_button(parent, options, text_label="", x=0, y=0, select=0):
    v = IntVar()
    local_parent = parent
    x_local = x
    y_local = y
    if text_label != "":
        label_frame = LabelFrame(parent, text=text_label,padx=5, pady=0)
        label_frame.grid(row=x,column=y)
        local_parent = label_frame
    for i in range(0, len(options)):
        exec("radio" + str(i) + " = Radiobutton(local_parent, text='" + str(options[i]) + 
            "', padx = 20, variable=v, value=" + str(i) +")")
        exec("radio" + str(i) + ".grid(row=x_local, column=y_local+i)")
        if select == i:
            exec("radio" + str(i) + ".select()")
    return [v, options]

def  msg(title, text, type="info", command_true=None, command_false=None):
    """showinfo()
    showwarning()
    showerror()
    askquestion()
    askokcancel()
    askyesno()
    askretrycancel()"""
    types = ["info", "warning", "error", "question", "okcancel", "yesno", "retrycancel"]
    functions = ["showinfo", "showwarning", "showerror", "askquestion", "askokcancel", "askyesno", "askretrycancel"]
    funct = {}
    for i in range(0, len(types)-1):
        funct[types[i]] = functions[i]
    if command_true != None and command_false != None:
        if eval(funct[type] + "(\"" + title + "\", \"" + text + "\")"):
            command_true
        else:
            command_false
    else:
        exec(funct[type] + "(\"" + title + "\", \"" + text + "\")")

