import time
import xlsxwriter
import csv
import win32com.client

def log(log_object, message, progress=0, term=False, function=None, close=False):
    if log_object == None or term == True:
        print("{} => {}".format(function, message))
    else:
        log_object.add_log(message, progress=progress, function=function, close=close) 

"""Pour gérer le temps, on importe le module time
On va utiliser surtout la fonction time() de ce module qui renvoie le nombre
de secondes écoulées depuis le premier janvier 1970 (habituellement).
On va s'en servir pour calculer le temps mis par notre fonction pour
s'exécuter"""

def log_display(display_time=False, message=""):
        def decorator(function_to_execute):
                """Notre décorateur. C'est lui qui est appelé directement LORS
                DE LA DEFINITION de notre fonction (fonction_a_executer)"""

                def modified_function(*args, **kwargs):
                        """Fonction renvoyée par notre décorateur. Elle se charge
                        de calculer le temps mis par la fonction à s'exécuter"""
                        print(message)
                        if display_time == True:
                                time_before = time.time() # avant d'exécuter la fonction
                                ret = function_to_execute(*args, **kwargs)
                                time_after = time.time()
                                time_execution = time_after - time_before
                                print("{0} => {1} s to execute".format(function_to_execute, \
                                                                                round(time_execution, 4)))
                        else:
                                ret = function_to_execute(*args, **kwargs)
                        return ret
                return modified_function
        return decorator


def excel_export(file_path, result_tab=[], field_names=[]):
        # Create a workbook and add a worksheet.
        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet()

        columns = len(field_names)
        rows = len(result_tab)
        
        # Start from the first cell. Rows and columns are zero indexed.
        x = 0
        y = 0

        # Iterate over the data and write it out row by row.
        for field in field_names:
            worksheet.write(x, y, field)
            y += 1

        # Iterate over the data and write it out row by row.
        for row in range(rows):
            for column in range(columns):
                worksheet.write(row+1, column, str(result_tab[row][column]))
        workbook.close()
        try:
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = False
            workbook = excel.Workbooks.Open(file_path)
            excel.Visible = True
            return True
        except Exception as e:
            return False


def csv_export(file_path, result_tab=[], field_names=[]):
        with open(file_path, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(field_names)
            #writer.writeheader()
            for row in result_tab:
                writer.writerow(list(row))

def json_export(file_path, result_tab=[], field_names=[]):
        if result_tab != []:
                dict_json = {}
                with open(file_path, "w") as json_file:
                        string = "[ "
                        json_file.write(string)
                        i = 0
                        for row in result_tab:
                                string = "{ "
                                for j in range(0, len(field_names)):
                                        string += "\"{}\" : \"{}\"".format(field_names[j], str(row[j]).replace("\"", "\\\""))
                                        if j < len(field_names) - 1:
                                                string += ", "
                                        dict_json[field_names[j]] = row[j]
                                string += "}"
                                if i < len(result_tab) - 1:
                                        string += ", \n"
                                json_file.write(string)
                                i += 1
                        json_file.write("]")
                        print("Nb of rows : {}".format(len(result_tab)))
                return dict_json