from tkinter import *
import Pmw
from app_settings import *
from app_dictionary import _, load_dictionary


class AppToolBar(Frame):

    def __init__(self, parent=None, app_main=None, app_federation=None, x=0, y=0):
        Frame.__init__(self, parent, bd=1)
        images =('new_fed','open_federation','save_federation','add_mysql','add_postgres',
                'add_sqlite','add_excel','add_csv','add_json','add_api','add_xml','settings','exit')
        textes =(_('New data federation'),_('Open Data Federation'),_('Save Data Federation'),
                _('Add MySQL database'),_('Add PostgreSQL database'),_('Add SQLite database'),
                _('Add Excel file'),_('Add CSV file'),_('Add json file'),_('Add rest api'),
                _('Add XML file'),_('Settings'),_('Exit'))
        self.app_main = app_main
        self.app_federation = app_federation
        # Création d'un objet <bulle d'aide> (un seul suffit) :
        tip = Pmw.Balloon(self)
        # Création de la barre d'outils (c'est un simple cadre) :
        #toolbar = Frame(self, bd =1)
        #toolbar.pack(side = TOP, expand =YES, fill =X)
        self.grid(row = x,column = y)
        # Nombre de boutons à construire : 
        nBou = len(images)
        # Les icônes des boutons doivent être placées dans des variables
        # persistantes. Une liste fera l'affaire :
        self.photoI =[None]*nBou
        
        for b in range(nBou):
            # Création de l'icône (objet PhotoImage Tkinter) :
            self.photoI[b] =PhotoImage(file = 'img/' + images[b] +'.png')
            
            # Création du bouton.:
            # On utilise une expression "lambda" pour transmettre
            # un argument à la méthode invoquée comme commande :
            bou = Button(self, image =self.photoI[b], relief =GROOVE,
                         command = lambda arg =b: self.tool_bar_action(arg))
            bou.pack(side =LEFT)
            
            # association du bouton avec un texte d'aide (bulle) :
            tip.bind(bou, textes[b]) 

    def tool_bar_action(self, b):
        self.champ_federation = StringVar()
        if b == 0:
            self.app_federation.new_federation()
        if b == 1:
            self.app_federation.restore_fed_and_queries()
        if b == 2:
            self.app_federation.save_federation_name()
        if b == 3:
            self.app_federation.add_db_source(type="MYSQL")
        if b == 4:
            self.app_federation.add_db_source(type="POSTGRES") 
        if b == 5:
            self.app_federation.add_sqlite_source()    
        if b == 6:
            self.app_federation.add_file_source(type="EXCEL")
        if b == 7:
            self.app_federation.add_file_source(type="CSV")
        if b == 8:
            self.app_federation.add_file_source(type="JSON")
        if b == 9:
            self.app_federation.add_file_source(type="API")
        if b == 10:
            self.app_federation.add_file_source(type="XML")
        if b == 11:
            settings = AppSettings(self.app_main)
        if b == 12:
            self.app_main.destroy()