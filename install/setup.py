"""Fichier d'installation de notre script salut.py."""

from cx_Freeze import setup, Executable
import os.path

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

base = "Win32GUI"
#base = "Console"

packages = ["idna", "pmw"]

options = {
    'build_exe': {
        'include_files':[
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
         ],
         'packages':packages,
    },
}


# On appelle la fonction setup
setup(
    name = "odataf",
    options = options,
    version = "1.41.0",
    author = "Laurent ESTIEVE",
    description = "Open DATA Federator",
    executables = [Executable("odataf.py", base=base)],
)