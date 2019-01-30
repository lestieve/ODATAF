import pytablereader
import simplesqlite
import sqlite3
import urllib.request, json 
import mysql.connector
import psycopg2
#import magic
from odf_table import *
from odf_tools import *
from app_log import *

class Source: 
    """Classe définissant une source :
    - type : son type (EXCEL, CSV, JSON, MYSQL,...)
    - id : source id (il peut y avoir plusieurs sources du même type)
    - name : son nom
    - tables : liste de tables
    - tables_name : liste de tables accessible par nom"""
        
    def __init__(self, federation, type, id, name):
        """Constructeur
        - type : son type (EXCEL, CSV, JSON, MYSQL,...)
        - id : source id (il peut y avoir plusieurs sources du même type)
        - name : son nom"""
        self.federation = federation
        self.general_type = ""
        self.type = str(type).upper()
        self.id = id
        if name != "":
            self.name = name
        else:
            self.name = "{} source {}".format(self.type, self.id)
        self.source_name = "{}{}".format(self.type, self.id)
        self.tables = []
        self.tables_name = {}


class FileSource(Source): 
    """Classe définissant une source de fichier héritant de la classe Source :
    - file_path : chemin vers le fichier
    - loader : pour fichiers Excel et csv
    - data : pour Json"""
        
    def __init__(self, federation, type, id, name, file_path, table_name = ""): 
        """Constructeur
        - type : son type (EXCEL, CSV, JSON, MYSQL,...)
        - id : source id (il peut y avoir plusieurs sources du même type)
        - name : son nom
        - file_path : chemin vers le fichier"""
        Source.__init__(self, federation, type, id, name)
        self.general_type = "FILE"
        self.host = ""
        self.user = ""
        self.password = ""
        self.database = ""
        self.port = ""
        self.file_path = file_path
        self.table_name = table_name
        self.add_table_to_list()

    @log_display(display_time=True, message="## Import into SQLITE TEMP DB ##")            
    def data_to_sqlite(self, con, query_tables = [], log_app=None, limit=None, reload=False):
        """Chargement d'un fichier en sqlite
        - con : connexion à une base sqlite""" 
        self.log = log_app
        self.reload=reload
        tables_name = []
        for table in query_tables:
            tables_name.append(table.target_name)
            print("Table to load : {}".format(table.target_name))

        if self.type == "EXCEL":
            for table_data in self.loader.load():
                if table_data.table_name.replace(" ", "_") in tables_name:
                    if table_data.table_name.replace(" ", "_") not in self.federation.sources_loaded or self.reload == True:
                        con.create_table_from_tabledata(table_data)
                        log(self.log, "# {} Excel sheet loaded".format(table_data.table_name.replace(" ", "_")), function="FileSource.data_to_sqlite")
                        self.federation.add_source_loaded(table_data.table_name.replace(" ", "_"))
                    else:
                        log(self.log, "# {} Excel sheet already loaded".format(table_data.table_name.replace(" ", "_")), function="FileSource.data_to_sqlite")
        elif self.type == "CSV":
            if self.tables[0].target_name not in self.federation.sources_loaded or self.reload == True:
                con.create_table_from_csv(self.file_path,table_name=self.tables[0].target_name, delimiter=self.delimiter)
                log(self.log, "# {} CSV data loaded".format(self.tables[0].target_name), function="FileSource.data_to_sqlite")
                self.federation.add_source_loaded(self.tables[0].target_name)
            else:
                log(self.log, "# {} CSV data already loaded".format(self.tables[0].target_name), function="FileSource.data_to_sqlite")
        elif self.type == "JSON":
            if self.tables[0].target_name not in self.federation.sources_loaded or self.reload == True:
                con.create_table_from_json(self.data,table_name=self.tables[0].target_name)
                log(self.log, "# {} JSON data loaded".format(self.tables[0].target_name), function="FileSource.data_to_sqlite")
                self.federation.add_source_loaded(self.tables[0].target_name)
            else:
                log(self.log, "# {} JSON data already loaded".format(self.tables[0].target_name), function="FileSource.data_to_sqlite")
        elif self.type == "API":
            if self.tables[0].target_name not in self.federation.sources_loaded or self.reload == True:
                con.create_table_from_json(self.data,table_name=self.tables[0].target_name)
                log(self.log, "# {} API data loaded".format(self.tables[0].target_name), function="FileSource.data_to_sqlite")
                self.federation.add_source_loaded(self.tables[0].target_name)
            else:
                log(self.log, "# {} API data already loaded".format(self.tables[0].target_name), function="FileSource.data_to_sqlite")
        
    @log_display(display_time=True, message="## Adding tables and fields lists ##")
    def add_table_to_list(self):
        """Ajout de la liste des tables dans l'attribut tables[]"""
        self.tables = []
        self.tables_name = {}
        if self.type == "EXCEL":
            self.loader = pytablereader.ExcelTableFileLoader(self.file_path)
            self.data = None
        elif self.type == "CSV":
            self.loader = pytablereader.CsvTableFileLoader(self.file_path)
            self.delimiter = self.delimiter_selection(self.file_path)
            """try:
                self.encoding = self.encoding_type(self.file_path)
            except:
                pass"""
            self.loader.delimiter = self.delimiter
            self.data = None
        elif self.type == "JSON":
            with open(self.file_path, 'r') as file:
                data = json.loads(file.read())
                self.data = json.dumps(data)
        elif self.type == "API":
            with urllib.request.urlopen(self.file_path) as url:
                data = json.loads(url.read().decode())
                self.data = json.dumps(data)
        if self.type == "EXCEL" or self.type == "CSV":
            for table_data in self.loader.load():
                self.tables.append(Table(self,table_data.table_name, table_data.header_list))
                self.tables_name[table_data.table_name] = Table(self,table_data.table_name, table_data.header_list)
                print("Adding {}".format(table_data.table_name))
        elif self.type == "JSON" or self.type == "API":
            header_list = json.loads(self.data)[0]
            self.tables.append(Table(self, self.table_name, header_list))
            self.tables_name[self.table_name] = Table(self,self.table_name, header_list)

    @log_display(display_time=False, message="## Delimiter identification ##")
    def delimiter_selection(self, file_path):
        with open(file_path, 'r') as file:
            text = file.read()
            comma = 0
            pcomma = 0
            if len(text) >= 1000:
                length = 1000
            else:
                length = len(text)
            i = 0 
            while i < length:
                if text[i] == ',':
                    comma += 1
                elif text[i] == ';':
                    pcomma += 1 
                i += 1
            if comma >= pcomma:
                print("Delimiter : ,")
                return ','
            else:
                print("Delimiter : ;")
                return ';'
        
    """def encoding_type(self, file_path):
        with open(file_path, 'r') as file:
            blob = file.read()
            m = magic.Magic(mime_encoding=True)
            encoding = m.from_buffer(blob)
            print(encoding)
            return encoding"""

class DBSource(Source): 
    """Classe définissant une source de base de données héritant de la class Source :
    - host : URL vers la base de données
    - user : user de connexion à la base
    - password : mot de passe de connexion à la base
    - database : database name"""
        
    def __init__(self, federation, type, id, name, host, user, password, database, port="", file_path=""): 
        """Constructeur
        - type : son type (EXCEL, CSV, JSON, MYSQL,...)
        - id : source id (il peut y avoir plusieurs sources du même type)
        - name : son nom
        - host : URL vers la base de données
        - user : user de connexion à la base
        - password : mot de passe de connexion à la base
        - database : database name"""
        Source.__init__(self, federation, type, id, name)
        self.general_type = "DB"
        self.file_path = file_path
        self.table_name = ""
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.add_table_to_list()

    @log_display(display_time=True, message="## Import into SQLITE TEMP DB ##")
    def data_to_sqlite(self, con, query_tables, sql="", table_name="", log_app=None, limit=None, reload=False):
        """Chargement d'une requête sur la base source dans la base sqlite
        - con : connexion à la base sqlite
        - sql : requête sur la base source
        - table_name : nom de la table cible recueillant les données"""
        self.log = log_app
        self.limit = limit
        self.reload = reload
        if query_tables != []:
            for table in query_tables:
                print("Table to load : {}".format(table.target_name))
                if table.source.type != "SQLITE":
                    if table.target_name not in self.federation.sources_loaded or self.reload == True:
                        if self.limit != None:
                            sql = "select * from {} limit {}".format(table.table_name, self.limit)
                        else:
                            sql = "select * from {}".format(table.table_name)
                        data = self.dbase_query_json(sql)
                        con.create_table_from_json(data,table_name=table.target_name)
                        log(self.log, "=> table {} loaded".format(table.target_name), function="DBSource.data_to_sqlite")
                        self.federation.add_source_loaded(table.target_name)
                    else:
                        log(self.log, "=> table {} already loaded".format(table.target_name), function="DBSource.data_to_sqlite")
        elif sql != "":
            result = self.dbase_query_json(sql)
            data = json.dumps(result)
            con.create_table_from_json(data,table_name=table_name)
        else:
            log(self.log, "Nothing to load", function="DBSource.data_to_sqlite")
        
    @log_display(display_time=False, message="## Connection to DB ##")
    def connection(self):
        if self.type == "MYSQL":
            con = mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.database)
            #except:
            #    self.add_log("MySQL connection error", 0)
            #    con = None
        elif self.type == "POSTGRES":
            con = psycopg2.connect(database=self.database, user=self.user, password=self.password, host=self.host, port=self.port)
            #except:
            #    self.add_log("MySQL connection error", 0)
            #    con = None
        elif self.type == "SQLITE":
            #try:
            con = sqlite3.connect(self.file_path)
            #except sqlite3.Error as e:
            #    print(e)
        return con

    @log_display(display_time=True, message="## Adding tables and fields lists ##")
    def add_table_to_list(self):
        self.tables = []
        self.tables_name = {}
        tables = []
        if self.type == "MYSQL":
            tables = self.dbase_query_list("show tables from {}".format(self.database))
        elif self.type == "POSTGRES":
            tables = self.dbase_query_list("select table_name from information_schema.tables where table_schema='public'")
        elif self.type == "SQLITE":
            tables = self.dbase_query_list("SELECT name FROM sqlite_master WHERE type='table'")
        for table in tables:
            if self.type == "MYSQL":
                columns = self.dbase_query_list("show fields from {}".format(table))
                self.tables.append(Table(self, table, columns))
                self.tables_name[table] = Table(self,table, columns)
            elif self.type == "POSTGRES":
                """select column_name, data_type, character_maximum_length \
                                                from INFORMATION_SCHEMA.COLUMNS \
                                                where table_name = '{}'"""
                columns = self.dbase_query_list("select column_name \
                                                from INFORMATION_SCHEMA.COLUMNS \
                                                where table_name = '{}'".format(table))
                self.tables.append(Table(self, table, columns))
                self.tables_name[table] = Table(self,table, columns)
            elif self.type == "SQLITE":
                rows = self.dbase_query_list("PRAGMA table_info({})".format(table[0]))
                columns = []
                for row in rows:
                    columns.append(row[1])
                self.tables.append(Table(self, table[0], columns))
                self.tables_name[table[0]] = Table(self, table[0], columns)
        
    @log_display(display_time=True, message="## Database to JSON ##")
    def dbase_query_json(self, sql):
        if self.type == "MYSQL":
            con = self.connection()
            data = []
            if con != None:
                cur = con.cursor()
                cur.execute(sql)
                columns = tuple( [d[0] for d in cur.description] )
                for row in cur:
                    data.append(dict(zip(columns, row)))
        result = json.dumps(data, default = str)
        return result
    
    @log_display(display_time=True, message="## Database to list ##")
    def dbase_query_list(self, sql):
        result = []
        con = self.connection()
        if self.type == "MYSQL":
            if con != None:
                cur = con.cursor()
                cur.execute(sql)
                for row in cur:
                    result.append(row[0])
        elif self.type == "POSTGRES":
            if con != None:
                cur = con.cursor()
                cur.execute(sql)
                for row in cur:
                    result.append(row[0])
        elif self.type == "SQLITE":
            cur = con.cursor()
            cur.execute(sql)
            result = cur.fetchall()
            con.close()
        return result
                 