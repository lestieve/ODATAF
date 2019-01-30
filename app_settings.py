from tkinter import *
from app_tools import *
from app_dictionary import _, load_dictionary

class AppSettings(Toplevel):

    def __init__(self, app_main):
        Toplevel.__init__(self)
        self.app_main = app_main
        self.title(_("Settings"))
        self.languages_list = list_box(self, text_label=_("Select language"), vbar=True, width=20, height=3)
        self.languages_list.insert(0, _("English"))
        self.languages_list.insert(1, _("French"))
        self.languages = ["en", "fr"]
        button(self, _("Save settings"), self.save_settings, x=1, y=2)

    def save_settings(self):
        for index in self.languages_list.curselection():
            self.app_main.lang = self.languages[index]
        self.app_main.save_settings()
        msg(_("Warning"), _("You must restart the application to take effect."), type="warning")
        self.destroy()
        