"""
VocabiPy.
"""

# from ttkwidgets.autocomplete import AutocompleteEntry
import tkinter as tk
import json
import customtkinter as ctk
import pyperclip as clip
import dictionarymethods as dt


class App(ctk.CTk):
    """
    This class places all the window's widgets of the app and defines
    most of their behaviors.
    """

    def __init__(self):
        # --------------------Main root Window--------------------#
        super().__init__()
        self.geometry("500x400")
        self.title("VocabiPy")
        self.iconbitmap("mainicon.ico")

        # --------------------Getting Settings-------------------#
        # Trying to open the settings json file and get its data.
        try:
            with open("./settings.json", encoding="utf-8") as file:
                file_settings = file.read()
        # If the settings file doesn't exist, it will create a new one.
        except FileNotFoundError:
            # This is just a different way to make a long string
            file_settings = (
                "{"
                + '"selected_font": "Fixedsys,12", '
                + '"language": "english", '
                + '"appearance_mode":"System"'
                + "}"
            )
            with open("./settings.json", "w", encoding="utf-8") as file:
                file.write(file_settings)

        self.settings = json.loads(file_settings)

        # This will call the selected_font.setter and process the string input.
        self.selected_font = self.settings["selected_font"]

        # --------------------Settings Frame--------------------#

        # settings frame for app settings
        self.settings_frame = ctk.CTkFrame(self, width=50)
        self.settings_frame.pack(fill=tk.X, side=tk.TOP, padx=2, pady=2)
        self.settings_frame.grid_columnconfigure(3, weight=1)
        self.settings_frame.grid_rowconfigure(1, weight=1)

        # --------------------Entry Frame--------------------#

        # entry frame containing the query input and search button
        self.entry_frame = ctk.CTkFrame(self, corner_radius=10)
        self.entry_frame.pack(pady=20)

        # --------------------Inside settings_frame--------------------#

        # button for copying the meaning to clipboard
        self.copy_meaning_button = ctk.CTkButton(
            self.settings_frame,
            text="Copy Meaning",
            font=self.selected_font,
            width=40,
            command=self.copy_meaning,
        )
        self.copy_meaning_button.grid(row=0, column=1, padx=5, pady=5, sticky="nswe")

        # change font option menu
        self.change_font_button = ctk.CTkButton(
            self.settings_frame,
            text="Change Font",
            font=self.selected_font,
            command=self.change_font,
        )
        self.change_font_button.grid(row=0, column=2, padx=5, pady=5, sticky="nswe")

        # "Workaround" so the first color value is the previously selected one.
        color_values = ["Dark", "Light", "System"]
        color_values.remove(self.settings["appearance_mode"])
        color_values = [self.settings["appearance_mode"]] + color_values

        # change theme option menu
        self.theme_menu = ctk.CTkOptionMenu(
            self.settings_frame,
            values=color_values,
            font=self.selected_font,
            command=self.change_theme,
        )
        self.theme_menu.grid(row=0, column=3, padx=5, pady=5, sticky="nswe")

        # --------------------Inside entry_frame--------------------#

        # taking the query input
        self.query_entry = ctk.CTkEntry(
            self.entry_frame,
            width=180,
            border_width=1,
            placeholder_text="Search word...",
            font=self.selected_font,
        )
        self.query_entry.grid(row=0, column=0, pady=5, padx=5)
        self.query_entry.bind("<Return>", self.search_meaning)

        # preferred language
        self.language_entry = ctk.CTkEntry(
            self.entry_frame,
            font=self.selected_font,
            width=80,
            placeholder_text="language",
        )
        self.language_entry.grid(row=0, column=1, pady=5, padx=5)
        self.language_entry.insert(0, self.settings["language"])

        # search for the meaning button
        self.search_button = ctk.CTkButton(
            self.entry_frame,
            text="Search",
            width=50,
            font=self.selected_font,
            command=self.search_meaning,
        )
        self.search_button.grid(row=0, column=2, pady=5, padx=5)

        # --------------------TextBox for displaying the meanings--------------------#
        self.search_results = tk.Text(
            self,
            font=self.selected_font,
            fg="white",
            bg="#303031",
            border=0,
            relief="flat",
        )
        self.search_results.pack(
            fill=tk.BOTH,
            expand=True,
            pady=10,
            padx=10,
            ipadx=10,
            ipady=10,
        )
        self.search_results.config(state="disabled")

        # Theme must only be changed after "search_results" is created.
        self.change_theme(self.settings["appearance_mode"])

        # running the app
        self.mainloop()

    @property
    def selected_font(self):
        """
        A property that returns the selected font.
        """
        return self._selected_font

    @selected_font.setter
    def selected_font(self, param):
        """
        Selected font's setter.
        It can receive either a tuple or a string as input.

        e.g.:
        self.selected_font = ("Arial", 12)
        self.selected_font = ("Arial",)
        self.selected_font = "Arial,12"
        self.selected_font = "Arial"
        """
        if isinstance(param, tuple) and len(param) == 2:
            self._selected_font = param
            return
        if isinstance(param, tuple) and len(param) == 1:
            self._selected_font = (param[0], 12)
        if isinstance(param, str) and "," in param:
            param = param.split(",")
            self._selected_font = (param[0], int(param[1]))
            return
        if isinstance(param, str) and "," not in param:
            self._selected_font = (param, 12)
            return

        raise TypeError(
            "Selected font should be a tuple or a string. Check docstring for more info."
        )

    # --------------------class App Attributes/Functions--------------------#
    def search_meaning(self, event=None):
        """
        This method inserts the searched meaning in the text box.
        """
        language_selected = self.language_entry.get()

        # Saving last language searched to file.
        self.settings["language"] = language_selected
        self.save_settings()

        self.search_results.config(state="normal")
        self.search_results.delete("1.0", tk.END)
        entry = self.query_entry.get()
        meaning_list = dt.meaning(entry)

        if len(meaning_list) != 1:
            for meanings in meaning_list:
                final_meaning = dt.translate(meanings, language_selected)
                if final_meaning == "Couldn't translate that!":
                    self.search_results.insert(tk.END, final_meaning)
                    return
                self.search_results.insert(tk.END, f"■  {final_meaning}\n\n")

        else:
            tips = (
                "Possible causes for error :- \n"
                + "    Check for Typos\n"
                + "    The word might not be available in the API"
            )
            self.search_results.insert(tk.END, f"{meaning_list[0]}\n\n{tips}")

        self.search_results.config(state="disabled")

    def change_theme(self, mode):
        """
        Change theme command.
        """
        ctk.set_appearance_mode(mode)
        self.settings["appearance_mode"] = mode
        self.save_settings()

        if mode == "Light":
            self.search_results.config(fg="#202020", bg="#dadada")

        else:
            self.search_results.config(fg="white", bg="#303031")

    def change_font(self):
        """
        Change font command.
        """
        # getting the name of the font
        font_name_input = ctk.CTkInputDialog(
            None,
            text="Enter font name...",
            title="Change Font",
        )

        self.selected_font = font_name_input.get_input()

        # Saving font to file. This way of saving allows the user to input the font
        # size as well. e.g. write Arial,20 in the input dialog.
        self.settings["selected_font"] = "{},{}".format(*self.selected_font)
        self.save_settings()

        # trying to change the font
        try:
            self.copy_meaning_button.configure(font=self.selected_font)
            self.change_font_button.configure(font=self.selected_font)
            self.theme_menu.configure(font=self.selected_font)
            self.query_entry.configure(font=self.selected_font)
            self.language_entry.configure(font=self.selected_font)
            self.search_button.configure(font=self.selected_font)
            self.search_results.configure(font=self.selected_font)

        except tk.TclError:
            error_message = "Couldn't change the font!"
            self.search_results.configure(state="normal")
            self.search_results.insert(tk.END, error_message)
            self.search_results.configure(state="disabled")

    def copy_meaning(self):
        """
        This method copies the meaning in the textbox into the user's
        clipboard.
        """
        meaning = self.search_results.get("1.0", "end")
        clip.copy(meaning)

    def save_settings(self):
        """
        This function saves the current state of the settings into
        the settings.json file.
        """
        with open("./settings.json", "w", encoding="utf-8") as file:
            file.write(json.dumps(self.settings))


app = App()
