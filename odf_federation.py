import pickle
from odf_source import *
from odf_query import * #Query, Filter, QueryField

class Federation: 
    """Class defining a data federation that groups together several sources"""
        
    def __init__(self,name):
        """Constructor
        
        Arguments:
            name {str} -- Name of the data federation
        """ 
        self.name = name
        self.sources = []
        self.sources_name = {}
        self.joins = []
        self.queries = []
        self.queries_results = []
        self.sources_loaded = []
        self.sqlite_path = "TEMP.sqlite"
        self.save_path = ""
        
    def add_source(self, source):
        """Adding a source (object type)
        
        Arguments:
            source {source object} -- source to add
        """
        self.sources.append(source)
        self.sources_name["{}{}".format(source.type, source.id)] = source

    def add_source_loaded(self, source):
        self.sources_loaded.append(source)
        self.sources_loaded=list(dict().fromkeys(self.sources_loaded).keys()) 

    def update_source(self, source_index, name, file_path=""):
        """Modification d'une source (de type objet)
        - source_index : objet source"""
        self.sources[source_index].name = name
        if file_path != "":
            self.sources[source_index].file_path = file_path
        self.sources_name[self.sources[source_index].source_name] = self.sources[source_index]

    def delete_source(self, source_index):
        """Modification d'une source (de type objet)
        - source_index : objet source"""
        nb = len(self.joins)
        j = 0
        for i in range(0 , nb):
            if self.joins[j].left_source == self.sources[source_index].name or \
                self.joins[j].right_source == self.sources[source_index].name:
                del self.joins[j]
            else:
                j += 1
        del self.sources_name["{}{}".format(self.sources[source_index].type, self.sources[source_index].id)]
        del self.sources[source_index]

    def add_join(self, join):
        """Ajout d'une jointure (de type objet)
        - join : objet join"""
        self.joins.append(join)
        #self.sources_name[source.name] = source
    
    def add_query(self, query):
        """Ajout d'une requête (de type objet)
        - query : objet Query"""
        self.queries.append(query)
    
    def list_sources_tables_fields(self):
        """Liste des tables et des champs"""
        for source in self.sources:
            print("### Source : {} ({})".format(source.name,source.type))
            print()
            for table in source.tables:
                print("  => Table : {}".format(table.table_name))
                for field in table.fields:
                    print("     - {}".format(field.field_name))
                print()
            print()

    def save_federation(self, filename):
        self.save_path = filename
        with open(filename, 'wb') as file:
            my_pickler = pickle.Pickler(file)
            my_pickler.dump(self.name)
            my_pickler.dump(self.sqlite_path)
            my_pickler.dump(self.save_path)
            sources_list = []
            for source in self.sources:
                sources_list.append([source.general_type,
                                        source.type,
                                        source.id,
                                        source.name,
                                        source.file_path,
                                        source.table_name,
                                        source.host,
                                        source.user,
                                        source.password,
                                        source.database])
            my_pickler.dump(sources_list)
            joins_list = []
            for join in self.joins:
                joins_list.append([join.name,
                                    join.left_source, 
                                    join.left_table,
                                    join.left_table_target, 
                                    join.left_key,
                                    join.right_source, 
                                    join.right_table,
                                    join.right_table_target,
                                    join.right_key, 
                                    join.join_type])
            my_pickler.dump(joins_list)
        print("Federation : save success")
        #except:
        #    print("Save failure")
    
    def save_queries(self, filename):
        #try:
        self.save_federation(filename)
        with open(filename, 'ab') as file:
            my_pickler = pickle.Pickler(file)
            i = 0
            queries = []
            for query in self.queries:
                query_fields = []
                for field in query.query_fields:
                    query_fields.append((field.table.source.source_name,
                                    field.table.table_name,
                                    field.field_name,
                                    field.alias,
                                    field.field_type,
                                    field.agregate_fct))
                query_filters = []
                for filter in query.query_filters:
                    query_filters.append((filter.field.table.source.source_name,
                                    filter.field.table.target_name,
                                    filter.field.field_name,
                                    filter.filter_type,
                                    filter.filter_values,
                                    filter.description))
                query_joins = []
                for join in query.query_joins:
                    query_joins.append((join.name,
                                        join.left_source, 
                                        join.left_table,
                                        join.left_table_target, 
                                        join.left_key,
                                        join.right_source, 
                                        join.right_table,
                                        join.right_table_target,
                                        join.right_key, 
                                        join.join_type))
                queries.append((query.query_id, query.query_name, query.agregate, query.limit,
                                query_fields, query_filters, query_joins))
            i += 1
            my_pickler.dump(queries)
            results_name = []
            results_rows = []
            results_fields = []
            for result in self.queries_results:
                results_name.append(result[0])
                results_rows.append(result[1])
                results_fields.append(result[2])
            my_pickler.dump(results_name)
            my_pickler.dump(results_rows)
            my_pickler.dump(results_fields)

            print("Queries : save success")

    def restore_federation(self, filename):
        #try:
        with open(filename, 'rb') as file:
            my_depickler = pickle.Unpickler(file)
            # Suppression des sources et des jointures
            nb = len(self.sources)
            for i in range(0 , nb):
                self.delete_source(0)
            nb = len(self.joins)
            for i in range(0 , nb):
                del self.joins[0]
            self.name = my_depickler.load()
            self.sqlite_path = my_depickler.load()
            self.save_path = my_depickler.load()
            sources = my_depickler.load()
            i = 0
            for i in range(0, len(sources)):
                try:
                    source = None
                    if sources[i][0] == "FILE":
                        source = FileSource(self, sources[i][1], sources[i][2], sources[i][3], 
                                            sources[i][4], table_name=sources[i][5])
                    elif sources[i][0] == "DB":
                        source = DBSource(self, sources[i][1], sources[i][2], sources[i][3],
                                                sources[i][6], sources[i][7], sources[i][8], sources[i][9], file_path=sources[i][4])            
                    self.add_source(source)
                except FileNotFoundError:
                    print("File {} not found. The source is ignored.".format(sources[i][4]))
                except:
                    print("Can't access to {} source. This source is ignored.".format(sources[i][3]))
                i += 1
            i = 0
            joins = my_depickler.load()
            for i in range(len(joins)):
                join = None
                join = Join(joins[i][1], joins[i][2], joins[i][3], 
                                joins[i][4], joins[i][5], joins[i][6], 
                                joins[i][7], joins[i][8], joins[i][9])   
                try:
                    print("Sources ({} and {}) exist for this join : OK, adding join.".format(self.sources_name[joins[i][1]].source_name, self.sources_name[joins[i][5]].source_name))
                    self.add_join(join)
                except:
                    print("This join has been rejected because it needs an ignored source ({} or {}).".format(joins[i][1], joins[i][5]))
                    pass
                i += 1

            """ Restore Queries """
            nb = len(self.queries)
            for i in range(0 , nb):
                del self.queries[0]

            queries = my_depickler.load()
            i = 0
            for query in queries:
                try:
                    query_id = query[0]
                    query_name = query[1]
                    query_agregate = query[2]
                    query_limit = query[3]
                    # query_fields
                    query_fields = []
                    j=0
                    for j in range(0, len(query[4])):
                        print(self.sources_name[query[4][j][0]].source_name)
                        print(self.sources_name[query[4][j][0]].tables_name[query[4][j][1]].target_name)
                        print(self.sources_name[query[4][j][0]].tables_name[query[4][j][1]].fields_name[query[4][j][2]].field_name)
                        query_fields.append(QueryField(self.sources_name[query[4][j][0]].tables_name[query[4][j][1]], 
                                            self.sources_name[query[4][j][0]].tables_name[query[4][j][1]].fields_name[query[4][j][2]].field_name, 
                                            alias=query[4][j][3], field_type=query[4][j][4], agregate_fct=query[4][j][5]))
                        j += 1
                    # filters
                    query_filters = []
                    j=0
                    for j in range(0, len(query[5])):
                        query_filters.append(Filter(self.sources_name[query[5][j][0]].tables_name[query[5][j][1]].fields_name[query[5][j][2]],
                                                query[5][j][3], filter_values=query[5][j][4],
                                                description=query[5][j][5]))
                        j += 1
                    # joins
                    query_joins = []
                    j=0
                    for j in range(0, len(query[6])):
                        query_joins.append(Join(query[6][j][1], query[6][j][2], 
                                                    query[6][j][3], query[6][j][4], query[6][j][5], 
                                                    query[6][j][6], query[6][j][7], query[6][j][8], 
                                                    query[6][j][9]))
                        j += 1
                    """ enregistrement de la query """
                    self.queries.append(Query(self, query_fields, query_joins, query_filters, agregate=query_agregate, limit=query_limit, 
                            query_name=query_name))
                except:
                    print("A source is missing : the query can't be loaded.")
                i += 1
            try:
                results_name = my_depickler.load()
                results_rows = my_depickler.load()
                results_fields = my_depickler.load()
                for i in range(0, len(results_name)):
                    self.queries_results.append([results_name[i], results_rows[i], results_fields[i]])
            except:
                print("Restore error")

    def find_joins(self, fields_list):
        """ Recherche des jointures de la fédération à appliquer 
        - fields_list : liste d'objet Field"""
        id_joins = []       
        for field1 in fields_list:
            for field2 in fields_list:
                if "{}.{}".format(field1.table.target_name, field1.field_name) != "{}.{}".format(field2.table.target_name, field2.field_name):
                    id_joins.append(find_id_join(field1.table.target_name,field2.table.target_name))
        #id_joins = list(set(id_joins))
        id_joins = list(dict().fromkeys(id_joins).keys()) 
        joins_list = []
        for id_join in id_joins:
            for join in self.joins:
                if id_join == join.id_join:
                    joins_list.append(join)
        #joins_list = list(set(joins_list))
        joins_list = list(dict().fromkeys(joins_list).keys()) 
        return joins_list

class Join:
    """Classe définissant une jointure et regroupant plusieurs sources :
    - left_table : nom de la table à gauche
    - left_keys[] : liste des clés à gauche
    - right_table : nom de la table à droite
    - right_keys[] : liste des clés à droite
    - join_type : type de jointure (INNER, LEFT, RIGHT)
    - name : nom de la jointure (table left - table right)"""
        
    def __init__(self, left_source, left_table, left_table_target, left_key, 
                right_source, right_table, right_table_target, right_key, join_type):
        """Constructeur
        - left_table : nom de la table à gauche
        - left_keys[] : liste des clés à gauche
        - right_table : nom de la table à droite
        - right_keys[] : liste des clés à droite
        - join_type : type de jointure (INNER, LEFT, RIGHT)""" 
        self.left_source = left_source
        self.left_table = left_table
        self.left_table_target = left_table_target
        self.left_key = left_key
        self.right_source = right_source
        self.right_table = right_table
        self.right_table_target = right_table_target
        self.right_key = right_key
        self.join_type = join_type
        self.name = "{}.{} <={}=> {}.{}".format(self.left_table_target, 
                        self.left_key, self.join_type, self.right_table_target, self.right_key)
        self.id_join = find_id_join(self.left_table_target, self.right_table_target)


def find_id_join(table_field1, table_field2):
    tables_list = [table_field1, table_field2]
    tables_list.sort()
    print("-".join(tables_list))
    return "-".join(tables_list)   