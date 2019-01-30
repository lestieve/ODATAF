#from federation import *
import simplesqlite
import sqlite3
from sqlite3 import Error
import xlsxwriter
import csv
import win32com.client
from odf_table import *
from odf_tools import *

class Query: 
    """Classe définissant une requête :
    - query_fields : liste de champs de la requête
    - query_filters : liste de filtres
    - joins : liste de jointures
    - sqlite_path : chemin vers la base sqlite
    - sql : requête SQL (facultatif)
    - query_sources : sources nécessaires à la requête
    - query_tables : liste des tables pour le from"""
    queries_number = 0
    saved_queries = 0

    def __init__(self, federation, query_fields, query_joins, query_filters, sql = "", 
                agregate=False, limit=None, log=None, reload=False, query_name="", save_query=False):
        """Constructeur
        - fields : liste de champs de la requête
        - query_filters : liste de filtres
        - query_joins : liste de jointures
        - sqlite_path : chemin vers la base sqlite
        - sql : requête SQL (facultatif)"""
        Query.queries_number += 1
        if save_query == True:
            Query.saved_queries += 1
            self.query_id = Query.saved_queries
        else:
            self.query_id = Query.queries_number
        if query_name == "":
            self.query_name = "Query n°{}".format(self.query_id)
        else:
            self.query_name = query_name
        self.federation = federation
        self.query_fields = query_fields
        self.query_filters = query_filters
        self.query_joins = query_joins
        self.sql = sql
        self.agregate = agregate
        
        self.query_sources = []
        self.query_tables = []
        self.query_result = []
        self.limit = limit
        self.log = log
        self.reload = reload
 
        if save_query == True:
            self.federation.add_query(self)

    @log_display(display_time=False, message="## Sources to load ##")
    def list_sources_tables(self):
        """Liste des sources utilisées"""
        for field in self.query_fields:
            self.query_sources.append(field.table.source)
            self.query_tables.append(field.table)
        for filter in self.query_filters:
            self.query_sources.append(filter.field.table.source)
            self.query_tables.append(filter.field.table)
        # Suppression des doublons
        self.query_sources=list(dict().fromkeys(self.query_sources).keys()) 
        self.query_tables=list(dict().fromkeys(self.query_tables).keys()) 
        if len(self.query_sources) == 1 and self.query_sources[0].general_type == "DB" and self.query_sources[0].type != "SQLITE":
            self.sql_type = self.query_sources[0].type
        else:
            self.sql_type = "SQLITE"
        print("## Sources to load")
        log(self.log, "## Sources to load :", function="Query.list_sources_tables")
        for source in self.query_sources:
            log(self.log, "- {}".format(source.name), function="Query.list_sources_tables")
        log(self.log, "## Sources list to load OK", progress=5, function="Query.list_sources_tables")
        
    @log_display(display_time=True, message="## Loading sources ##")
    def load_sources(self):
        """Chargement en sqlite des sources utilisées
        - sqlite_path : chemin vers la base sqlite"""
        # create table ---
        #print("## Loading sources ##")
        if Query.queries_number == 1:
            mode = "w"
        else:
            mode = "a"

        con = simplesqlite.SimpleSQLite(self.federation.sqlite_path, mode)

        for source in self.query_sources:
            if source.type != "SQLITE":
                source.data_to_sqlite(con,self.query_tables, log_app=self.log, limit=self.limit, reload=self.reload)
                print("####")

        con.close()

    @log_display(display_time=True, message="## Query execution ##")
    def execute(self):
        try:
            """ Préparation des tables """
            self.list_sources_tables()
            log(self.log, "## Data preparation", function="Query.execute")
            if self.sql_type == "SQLITE":
                log(self.log, "=> Loading sources...", function="Query.execute")
                self.load_sources()
                log(self.log, "=> Sources loaded", progress=35, function="Query.execute")
            else:
                log(self.log, "=> Accessing directly to DB", progress=35, function="Query.execute")
            if self.sql == '':
                log(self.log, "=> SQL generation", function="Query.execute")
                self.sql = self.sql_generation()
                log(self.log, "=> SQL generated", progress=20, function="Query.execute")
            log(self.log, "## Data preparation OK", function="Query.execute")
            
            """Lancement de la requête"""
            log(self.log, "## Generating data results", function="Query.execute")
            if self.sql_type != "SQLITE":
                con = self.query_sources[0].connection()
            else:
                con = sqlite3.connect(self.federation.sqlite_path)
                # Attachement des sources SQLITE (s'il y'en a)
                self.attach_sqlite_sources(con)
            # Execution de la requete
            cur = con.cursor()
            cur.execute(self.sql)
            self.query_result = cur.fetchall()
            con.close()
            log(self.log, "## Data results generated", progress=20, function="Query.execute")
            return True
        except Exception as e:
            log(self.log, "KO => {}".format(e), function="Query.execute")
            return False

    @log_display(display_time=False, message="## SQL generation ##")
    def sql_generation(self):
        """Génération du code SQL de la requête"""
        # Création du dictionnaire de jointures
        """ On regroupe les jointures par table_left"""
        print("## SQL generation ##")
        dict_sql = {}
        """ SELECT """
        dict_sql["SQLITE", "SELECT"] = "\"'{}'.'{}' \".format(field.table.target_name, field.field_name)"
        dict_sql["MYSQL", "SELECT"] = "\"{}.{} \".format(field.table.table_name, field.field_name)"
        dict_sql["POSTGRES", "SELECT"] = "\"{}.{} \".format(field.table.table_name, field.field_name)"
        """ AS1 """
        dict_sql["SQLITE", "AS1"] = "\" as '{}' \".format(field.alias)"
        dict_sql["MYSQL", "AS1"] = "\" as '{}' \".format(field.alias)"
        dict_sql["POSTGRES", "AS1"] = "\" as '{}' \".format(field.alias)"
        """ AS2 """
        dict_sql["SQLITE", "AS2"] = "\" as '{} of {}' \".format(field.agregate_fct, field.field_name)"
        dict_sql["MYSQL", "AS2"] = "\" as '{} of {}' \".format(field.agregate_fct, field.field_name)"
        dict_sql["POSTGRES", "AS2"] = "\" as '{} of {}' \".format(field.agregate_fct, field.field_name)"
        """ VALUE """
        dict_sql["SQLITE", "VALUE"] = "\"{}('{}'.'{}') \".format(field.agregate_fct, field.table.target_name, field.field_name)"
        dict_sql["MYSQL", "VALUE"] = "\"{}({}.{}) \".format(field.agregate_fct, field.table.table_name, field.field_name)"
        dict_sql["POSTGRES", "VALUE"] = "\"{}({}.{}) \".format(field.agregate_fct, field.table.table_name, field.field_name)"
        """ JOIN """
        dict_sql["SQLITE", "JOIN"] = "\" \" + str(join.left_table_target)"
        dict_sql["MYSQL", "JOIN"] = "\" \" + str(join.left_table)"
        dict_sql["POSTGRES", "JOIN"] = "\" \" + str(join.left_table)"
        """ LEFT """
        dict_sql["SQLITE", "LEFT"] = "\" LEFT JOIN {}\".format(join.right_table_target)"
        dict_sql["MYSQL", "LEFT"] = "\" LEFT JOIN {}\".format(join.right_table)"
        dict_sql["POSTGRES", "LEFT"] = "\" LEFT JOIN {}\".format(join.right_table)"
        """ RIGHT """
        dict_sql["SQLITE", "RIGHT"] = "\" RIGHT JOIN {}\".format(join.right_table_target)"
        dict_sql["MYSQL", "RIGHT"] = "\" RIGHT JOIN {}\".format(join.right_table)"
        dict_sql["POSTGRES", "RIGHT"] = "\" RIGHT JOIN {}\".format(join.right_table)"
        """ INNER """
        dict_sql["SQLITE", "INNER"] = "\" INNER JOIN {}\".format(join.right_table_target)"
        dict_sql["MYSQL", "INNER"] = "\" INNER JOIN {}\".format(join.right_table)"
        dict_sql["POSTGRES", "INNER"] = "\" INNER JOIN {}\".format(join.right_table)"
        """ ON """
        dict_sql["SQLITE", "ON"] = "\" ON '{}'.'{}' = {}.'{}'\".format(join.left_table_target, join.left_key, join.right_table_target, join.right_key)"
        dict_sql["MYSQL", "ON"] = "\" ON {}.{} = {}.{}\".format(join.left_table, join.left_key, join.right_table, join.right_key)"
        dict_sql["POSTGRES", "ON"] = "\" ON {}.{} = {}.{}\".format(join.left_table, join.left_key, join.right_table, join.right_key)"
        """ FROM """
        dict_sql["SQLITE", "FROM"] = "table.target_name"
        dict_sql["MYSQL", "FROM"] = "table.table_name"
        dict_sql["POSTGRES", "FROM"] = "table.table_name"
        """ WHERE """
        dict_sql["SQLITE", "WHERE1"] = "\" '{}'.'{}' {} \\\"{}\\\" \".format(filter.field.table.target_name, filter.field.field_name, filter.filter_type, filter.filter_values[0])"
        dict_sql["MYSQL", "WHERE1"] = "\" {}.{} {} \\\"{}\\\" \".format(filter.field.table.table_name, filter.field.field_name, filter.filter_type, filter.filter_values[0])"
        dict_sql["POSTGRES", "WHERE1"] = "\" {}.{} {} \\\"{}\\\" \".format(filter.field.table.table_name, filter.field.field_name, filter.filter_type, filter.filter_values[0])"
        dict_sql["SQLITE", "WHERE2"] = "\" '{}'.'{}' {} ({}) \".format(filter.field.table.target_name, filter.field.field_name, filter.filter_type, ','.join(values))"
        dict_sql["MYSQL", "WHERE2"] = "\" {}.{} {} ({}) \".format(filter.field.table.table_name, filter.field.field_name, filter.filter_type, ','.join(values))"
        dict_sql["POSTGRES", "WHERE2"] = "\" {}.{} {} ({}) \".format(filter.field.table.table_name, filter.field.field_name, filter.filter_type, ','.join(values))"
        dict_sql["SQLITE", "WHERE3"] = "\" '{}'.'{}' {} '{}' AND '{}' \".format(filter.field.table.target_name, filter.field.field_name, filter.filter_type, filter.filter_values[0], filter.filter_values[1])"
        dict_sql["MYSQL", "WHERE3"] = "\" {}.{} {} '{}' AND '{}' \".format(filter.field.table.table_name, filter.field.field_name, filter.filter_type, filter.filter_values[0], filter.filter_values[1])"
        dict_sql["POSTGRES", "WHERE3"] = "\" {}.{} {} '{}' AND '{}' \".format(filter.field.table.table_name, filter.field.field_name, filter.filter_type, filter.filter_values[0], filter.filter_values[1])"
        dict_sql["SQLITE", "WHERE4"] = "\" '{}'.'{}' {} '%{}%' \".format(filter.field.table.target_name, filter.field.field_name, filter.filter_type, filter.filter_values[0])"
        dict_sql["MYSQL", "WHERE4"] = "\" {}.{} {} '%{}%' \".format(filter.field.table.table_name, filter.field.field_name, filter.filter_type, filter.filter_values[0])"
        dict_sql["POSTGRES", "WHERE4"] = "\" {}.{} {} '%{}%' \".format(filter.field.table.table_name, filter.field.field_name, filter.filter_type, filter.filter_values[0])"
        """ GROUP """
        dict_sql["SQLITE", "GROUP"] = "\" '{}'.'{}'\".format(axys[i].table.target_name, axys[i].field_name)"
        dict_sql["MYSQL", "GROUP"] = "\" {}.{}\".format(axys[i].table.table_name, axys[i].field_name)"
        dict_sql["POSTGRES", "GROUP"] = "\" {}.{}\".format(axys[i].table.table_name, axys[i].field_name)"
        # Génération de la requête
        query = "SELECT "
        i = 1
        for field in self.query_fields:
            if field.field_type == "AXYS":
                query += eval(dict_sql[self.sql_type, "SELECT"])
                if field.alias != "":
                    query += eval(dict_sql[self.sql_type, "AS1"])
            elif field.field_type == "VALUE":
                """query += "{}({}.'{}') ".format(field.agregate_fct, field.table.target_name, 
                                                field.field_name)"""
                query += eval(dict_sql[self.sql_type, "VALUE"])
                if field.alias != "":
                    query += eval(dict_sql[self.sql_type, "AS1"])
                else:
                    query += eval(dict_sql[self.sql_type, "AS2"]) 
            if i < len(self.query_fields):
                query += ", "
            i+=1
        """ FROM et jointures """
        query += " FROM "
        if len(self.query_joins) == 0:
            i = 0
            for table in self.query_tables:
                if i < len(self.query_tables) and len(self.query_tables) > 1:
                    query += eval(dict_sql[self.sql_type, "FROM"])  + ", "
                else:
                    query += eval(dict_sql[self.sql_type, "FROM"])
                i+=1
        else:
            # Ajout des jointures
            i=0
            for join in self.query_joins:
                print(join.name)
                if i == 0:
                    query += eval(dict_sql[self.sql_type, "JOIN"])
                if join.join_type == "LEFT":
                    query += eval(dict_sql[self.sql_type, "LEFT"])
                elif join.join_type == "RIGHT":
                    query += eval(dict_sql[self.sql_type, "RIGHT"])
                else:
                    query += eval(dict_sql[self.sql_type, "INNER"])
                query += eval(dict_sql[self.sql_type, "ON"])
                i += 1
        """ Clause WHERE """
        if len(self.query_filters) > 0:
            query += " WHERE "
            i = 0
            for filter in self.query_filters:
                if i > 0:
                    query += " AND "
                if filter.filter_type in ["=", ">", ">=", "<", "<="]:
                    query += eval(dict_sql[self.sql_type, "WHERE1"])
                elif filter.filter_type in ["IN", "NOT IN"]:
                    values = []
                    for value in filter.filter_values:
                        values.append('"{}"'.format(value))
                    query += eval(dict_sql[self.sql_type, "WHERE2"])
                elif filter.filter_type in ["BETWEEN", "NOT BETWEEN"]:
                    query += eval(dict_sql[self.sql_type, "WHERE3"])
                elif filter.filter_type in ["LIKE", "NOT LIKE"]:
                    """query += " {}.{} {} '%{}%' ".format(eval(dict_sql[self.sql_type, "WHERE"]), 
                                            filter.field.field_name, filter.filter_type, 
                                            filter.filter_values[0])"""
                    query += eval(dict_sql[self.sql_type, "WHERE4"])
                i += 1
        """ GROUP BY """
        if self.agregate == True:
            axys = []
            for field in self.query_fields:
                if field.field_type == "AXYS":
                    axys.append(field)
            if len(axys) > 0:
                query += " GROUP BY "
            for i in range(0, len(axys)):
                query += eval(dict_sql[self.sql_type, "GROUP"])
                if i + 1 < len(axys):
                    query += ", "
        
        if self.limit != None:
            query += " LIMIT 0,{}".format(self.limit)
        log(self.log, query, function="Query.sql_generation")
        return query   
    
    @log_display(display_time=True, message="## SQL export ##")
    def sql_export(self, file_path, output_table="TABLE", result_tab=[], field_names=[], 
                    db_type="SQLITE", query_type="INSERT", set_fields=[], where_fields=[]):
        dict_field = {}
        i = 0
        for field in field_names:
            dict_field[field.field_name] = i
            i += 1
        dict_sql = {}
        fieldnames = ["'{}'".format(field.field_name) for field in field_names]
        setfields = ["'{}'".format(field.field_name) for field in set_fields]
        wherefields = ["'{}'".format(field.field_name) for field in set_fields]
        """ INSERT """
        if query_type == "INSERT":
            dict_sql["SQLITE", "INSERT", ""] = "\"{}.'{}' \".format(field.table.target_name, field.field_name)"
            dict_sql["MYSQL", "INSERT"] = "\"{}.{} \".format(field.table.table_name, field.field_name)"
            dict_sql["POSTGRES", "INSERT"] = "\"{}.{} \".format(field.table.table_name, field.field_name)"
            with open(file_path, 'w') as sqlfile:
                for row in result_tab:
                    row = ["'"+str(var)+"'" for var in row]
                    text = "INSERT INTO {} ".format(output_table)
                    if field_names != []:
                        text += "({}) ".format(",".join(fieldnames))
                    text += "VALUES({});\n".format(",".join(list(row)))
                    sqlfile.write(text)
        elif query_type == "UPDATE":
            with open(file_path, 'w') as sqlfile:
                for row in result_tab:
                    row = ["'"+str(var)+"'" for var in row]
                    text = "UPDATE {} SET ".format(output_table)
                    s_fields = []
                    w_fields = []
                    for field in set_fields:
                        s_fields.append("{} = {}".format(field.field_name, row[dict_field[field.field_name]]))
                    text += "{} ".format(",".join(s_fields))
                    if len(where_fields) > 0:
                        for field in where_fields:
                            w_fields.append("{} = {}".format(field.field_name, row[dict_field[field.field_name]]))
                        text += " WHERE {} ".format(" AND ".join(w_fields))
                    text += ";\n"
                    sqlfile.write(text)

    def attach_sqlite_sources(self, con):
        for source in self.query_sources:
            if source.type == "SQLITE":
                source_name = "{}{}".format(source.type, source.id)
                sql = "attach '{}' as {}".format(source.file_path, source_name)
                try:
                    cur = con.cursor()
                    cur.execute(sql)
                    log(self.log, "{} source attached".format(source_name), function="Query.attach_sqlite_sources")
                    #print("{} source attached".format(source_name))
                except sqlite3.Error as e:
                        print(e)

    def field_labels(self):
        lib_columns = []
        for field in self.query_fields:
            if field.alias == "":
                lib_columns.append(field.field_name)
            else:
                lib_columns.append(field.alias)
        return lib_columns


class Filter:
    """ Classe définissant un filtre :
    - field : champ sur lequel porte le filtre
    - filter_type : =, >, >=, <, <=, IN, NOT IN, BEETWEEN
    - filter_values : liste de valeurs. Si vide, c'est l'entry field qui est utilisé"""

    def __init__(self, field, filter_type, filter_values=[], description=""):
        """ Constructeur
        - field
        - filter_type
        - filter_values"""
        self.field = field
        self.filter_type = filter_type
        self.filter_values = filter_values
        if description == "":
            self.description = "{}.{} {} [{}]".format(self.field.table.target_name, self.field.field_name, self.filter_type, ",".join(list(self.filter_values)))
        else:
            self.description = description


class QueryField(Field):
    """ Classe définissant un champ de requête :
    - field : champ de la fédération
    - alias : alias du champ
    - field_type : AXYS ou VALUE
    - argregate_fct : fonction à utiliser en cas d'agrégation"""
    def __init__(self, table, field_name, field_type="AXYS", alias="", agregate_fct=""):
        Field.__init__(self, table, field_name)
        self.field_type = field_type
        self.alias = alias
        self.agregate_fct = agregate_fct

    def field_label(self):
        if self.agregate_fct != "":
                label = "{}({}.'{}') ".format(self.agregate_fct, self.table.target_name, 
                                                self.field_name)
        else:
            label = "{}.{}".format(self.table.target_name, self.field_name)
        if self.alias != "":
            label += " as <{}>".format(self.alias)
        return label
