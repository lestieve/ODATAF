

class Table: 
    """Classe définissant une table :
    - source : objet définissant les paramètres de connexion (fichier, flux ou table de base de données)
    - table_name : nom de la table source
    - to_sqlite : True : déjà chargé, False : pas encore chargé
    - fields[] : liste des champs de la table
    - fields_name{} : dictionnaire des champs de la table
    - target_name : son nom cible (nom apparaissant dans la base sqlite)"""

    
    def __init__(self, source, table_name, header_list):
        """Constructeur
        - source : objet définissant les paramètres de connexion (fichier, flux ou table de base de données)
        - table_name : nom de la table source
        - fields_name : liste des champs de la table"""
        self.source = source
        self.table_name = table_name
        self.fields = []
        self.fields_name = {}
        if self.source.type == "EXCEL":
            self.target_name = self.table_name
        elif self.source.type == "SQLITE":
            self.target_name = "{}{}.{}".format(self.source.type,self.source.id,self.table_name)
        else:
            self.target_name = "{}{}_{}".format(self.source.type,self.source.id,self.table_name)
        for field in header_list:
            self.fields.append(Field(self, field))
            self.fields_name[field] = Field(self, field)

class Field: 
    """Classe définissant un champ de table :
    - table : objet définissant la table contenant le champ
    - field_name : nom du champ
    - field_type : type de champ (numérique, string, date)"""

    
    def __init__(self, table, field_name):
        """Constructeur"""
        self.table = table
        self.field_name = field_name


        