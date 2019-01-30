import json
import pickle

dict_languages = {}
dict_lang = {}

def load_dictionary(dictionary_path="dictionary.json", binary_path="dictionary.dat", lang="fr"):
        """Load the dictionary from the file dictionary.dat (pickle)
        If it's not found, it tries to create a new dictionary.dat file from the other file
        dictionary.json (you can find it in "dictionary" directory)
        It generates two python dictionaries :
        - dict_languages : it contains all languages
        - dict_lang : it contains the selected language (from lang variable)

        Keyword Arguments:
            dictionary_path {str} -- path to dictionary.json (default: {"dictionary.json"})
            binary_path {str} -- path to dictionary.dat (default: {"dictionary.dat"})
            lang {str} -- language to load (default: {"fr"})
        """
        global dict_languages, dict_lang 
        if dict_lang == {}:
            dict_languages = load_binary()
            if dict_languages == {}:
                try:
                    with open(dictionary_path, 'r') as file:
                        data = json.loads(file.read())
                        for row in data:
                            word = row["en"]
                            for key, value in row.items():
                                dict_languages[(key, word)] = value
                    save_json_to_binary(dictionary=dict_languages, binary_path=binary_path)
                    print("Dictionary created...")
                except:
                    print(_("Put a dictionary.json file in the root directory."))
            else:
                print("Dictionary loaded...")
            # Chargement du dictionnaire pour la langue sélectionnée
            keys = []
            for key, value in dict_languages.items():
                if key[0] == lang:
                    dict_lang[key[1]] = value       

def save_json_to_binary(dictionary=dict_languages, binary_path="dictionary.dat"):
    """Save dict_languages to a pickle file defined by binary_path
    
    Keyword Arguments:
        dictionary {dict} -- dictionary to save (default: {dict_languages})
        binary_path {str} -- path to pickle file (default: {"dictionary.dat"})
    """
    with open(binary_path, 'wb') as file:
            my_pickler = pickle.Pickler(file)
            my_pickler.dump(dictionary)
            print("{} file created.".format(binary_path))

def load_binary(binary_path="dictionary.dat"):
    """Load the dictionary pickle file to a python dictionary (dict)
    
    Keyword Arguments:
        binary_path {str} -- path to the pickle dictionary file (default: {"dictionary.dat"})
    """
    try:
        with open(binary_path, 'rb') as file:
            my_depickler = pickle.Unpickler(file)
            dictionary = my_depickler.load()
            return dictionary
    except:
        return {}

def _(word):
    """Returns the translated word from the dict_lang python dict.
    If the word is not found, it returns the same word (in english)
    
    Arguments:
        word {str} -- word to translate
    """
    global dict_lang
    if dict_lang == {}:
        load_dictionary()
    try:
        word_result = dict_lang[word]
        return word_result
    except:
        return word
