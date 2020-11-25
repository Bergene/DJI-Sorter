import os
from os import path
import tkinter
import PySimpleGUI as sg
from json import (load as jsonload, dump as jsondump)

class Gui:

    def __init__(self):
        self.SETTINGS_FILE = path.join(os.getcwd(), r'settings_file.cfg')
        self.DEFAULT_SETTINGS = {'Files': True,
                                 'Dates': True,
                                 'Sorted': True,
                                 'Moved': True,
                                 'Duplicate': False,
                                 'AuthorOutput': True,
                                 'Silent': False,
                                 'Testrun': True,
                                 'C_Radio': True,
                                 'M_Radio': None,
                                 'theme': sg.theme('Reddit'),
                                 'out_text_color': "",
                                 'ML_color': "",
                                 'bkgrnd_color': "",
                                 'text_color': "",
                                 'button_color': "",
                                 'button_text_color': "",
                                 'input_color': "",
                                 'input_text_color': ""}
        self.SETTING_TO_ELEMENT_KEYS = {'Files': '_FILES_CB_',
                                             'Dates': '_DATES_CB_',
                                             'Sorted': '_SORTED_CB_',
                                             'Moved': '_MOVE_CB_',
                                             'Duplicate': '_DUPLI_CB_',
                                             'AuthorOutput': '_OUT_AUTHOR_',
                                             'Silent': '_SILENT_CB_',
                                             'Testrun': '_TEST_CB_',
                                             'C_Radio': '_r_copy_',
                                             'M_Radio': '_r_move_',
                                             'theme': '_theme_',
                                             'out_text_color': '_out_text_color_',
                                             'ML_color': '_ML_color_',
                                             'bkgrnd_color': '_bkgrnd_color_',
                                             'text_color': '_text_color_',
                                             'button_color': '_button_color_',
                                             'button_text_color': '_button_text_color_',
                                             'input_color': '_input_color_',
                                             'input_text_color': '_input_text_color_'}
        self.SETTINGS = None

        self.main_window = None
        self.main_window_location = (None, None)
        self.main_window_size = (None, None)
        self.main_window_center = (None, None)
        self.values = None
        self.event = None

        self.settings_window = None
        self.settings_window_location = (None, None)
        self.settings_window_size = (320, 310)
        self.popup_location = (None, None)
# ---------------- END __init__ ----------------------------- #

    def create_main_window(self):

        def FillerButton(text, size):
            return sg.Button(text, size, visible=True, border_width=0, button_color=(sg.theme_background_color(),sg.theme_background_color()))

        # self.set_theme()
        if self.SETTINGS is not None:
            self.set_theme()
            ML_color = self.SETTINGS["ML_color"]
        else:
            ML_color = None


        # ------ Menu Definition ------ #
        menu_def = [['&File', ['&Properties', 'Exit']],
                    ['Edit', ['Paste', ['Special', 'Normal', ], 'Undo'], ],
                    ['Help', 'About...'], ]
        # ----------------------------- #

        # ------ Layout Definition----- #
        layout = [
            [sg.Menu(menu_def),
            sg.Frame(layout=[
                [sg.Text("Input:   "), sg.In(r"", key="_input_", enable_events=True),
                    sg.FolderBrowse(key="_browse1_", enable_events=True)],
                [sg.Text("Output:"), sg.In(r"", key="_output_"),
                    sg.FolderBrowse(key="_browse2_")],
                ], title="File Destinations", relief=sg.RELIEF_SUNKEN, pad=((0, 0), (20, 0)))],
            [sg.Frame(layout=[
                [sg.Checkbox(" Add Author?", key="_AUTHOR_CB_", enable_events=True), sg.Checkbox('Recurse', key="_SUB_CB_", enable_events=True)],
                [sg.Text("Author:"), sg.In(key="_author_in_", disabled=True, size=(17, 1))]
                ], title="Options", relief=sg.RELIEF_SUNKEN),
            sg.Frame(layout=[
                [sg.Checkbox('JPG ', key="_JPG_CB_", default=True, enable_events=True),
                    sg.Checkbox('DNG', key="_DNG_CB_", default=True, enable_events=True)],
                [sg.Checkbox('MOV', key="_MOV_CB_", default=True, enable_events=True),
                    sg.Checkbox('CR2', key="_CR2_CB_", default=True, enable_events=True)],
                ], title="Formats", relief=sg.RELIEF_SUNKEN, pad=((60, 0), (0, 0)))
            ],
            [sg.Column([
                [],
                [sg.Frame(layout=[
                    [sg.B('Show Files', size=(8, 1)), sg.B('Move', size=(8, 1)), sg.B("Test", size=(8, 1), visible=False), sg.B("Clear", size=(8, 1))]
                ], title="", relief=sg.RELIEF_SUNKEN)]
            ])
            ],
    [sg.Multiline(key="_ML_", background_color=ML_color, autoscroll=True, size=(80, 17), pad=((0, 0), (0, 20)))]
        ]
        self.main_window = sg.Window('Main Application', layout, element_justification='center', finalize=True, location=self.main_window_location)
        return self.main_window
# ---------------- END main layout -------------------------- #

    def get_chkbox_val(self, values):
        formats = list()
        for ext, value in {"JPG": values['_JPG_CB_'], "DNG": values['_DNG_CB_'], "MOV": values['_MOV_CB_'], "CR2": values['_CR2_CB_']}.items():
            if value is True:
                formats.append(ext)
        return formats
# ---------------- END main methods ------------------------- #

    def create_settings_window(self):
        # ------ Layout Definition----- #
        layout = [
            [
                sg.Frame(layout=[
                    [sg.Checkbox('Files', key="_FILES_CB_", tooltip="List files found.", size=(5, 1), default=False),
                     sg.Checkbox('Sorted', key="_SORTED_CB_", tooltip="List files after sorting.", size=(5, 1), default=False)],
                    [sg.Checkbox('Dates', key="_DATES_CB_", tooltip="List files by date.", size=(5, 1), default=False),
                     sg.Checkbox('Moved', key="_MOVE_CB_", tooltip="List files when moved/copied.", size=(5, 1), default=True)],
                ], title='What to show', relief=sg.RELIEF_SUNKEN),
                sg.Frame(layout=[
                    [sg.Checkbox("Duplicates", key="_DUPLI_CB_",
                                 tooltip="Having this checked make a copy of the original with the author.")],
                     [sg.Checkbox("Show output", key="_OUT_AUTHOR_", tooltip="Lists files when edited.")]
                ], title='Author Options', relief=sg.RELIEF_SUNKEN, size=(5, 5))
            ],
            [
                sg.Frame(layout=[
                    [sg.Checkbox("Testrun", key="_TEST_CB_", size=(13, 1), default=True,
                                 tooltip="No files will be moved or copied if this is checked."),
                     sg.Radio("Move", key="_r_move_", group_id="RADIO1"),
                     sg.Radio("Copy ", key="_r_copy_", group_id="RADIO1")],
                    [sg.Checkbox("Silent transfer", key="_SILENT_CB_", size=(13, 1), default=False,
                                 tooltip="Having checked this there will be no transfer status bar.")],

                ], title='Other options', relief=sg.RELIEF_SUNKEN)
            ],
            [sg.Frame(layout=[
                [sg.Combo(sg.theme_list(), key='_theme_', pad=((8, 0), (0, 0))), sg.Text('Theme')],
                [sg.Input(self.SETTINGS["out_text_color"], key='_out_text_color_', pad=((8, 0), (0, 0)), size=(22, 1), visible=False), sg.Text('Output text color', visible=False)],
                [sg.Input(self.SETTINGS["ML_color"], key='_ML_color_', pad=((8, 0), (0, 0)), size=(22, 1), visible=False), sg.Text('Multiline color', visible=False)],
                [sg.Input(self.SETTINGS["bkgrnd_color"], key='_bkgrnd_color_', pad=((8, 0), (0, 0)), size=(22, 1), visible=False), sg.Text('Background color', visible=False)],
                [sg.Input(self.SETTINGS["text_color"], key='_text_color_', pad=((8, 0), (0, 0)), size=(22, 1), visible=False), sg.Text('Text color', visible=False)],
                [sg.Input(self.SETTINGS["button_color"], key='_button_color_', pad=((8, 0), (0, 0)), size=(22, 1), visible=False), sg.Text('Button color', visible=False)],
                [sg.Input(self.SETTINGS["button_text_color"], key='_button_text_color_', pad=((8, 0), (0, 0)), size=(22, 1), visible=False), sg.Text('Button text color', visible=False)],
                [sg.Input(self.SETTINGS["input_color"], key='_input_color_', pad=((8, 0), (0, 0)), size=(22, 1), visible=False), sg.Text('Input color', visible=False)],
                [sg.Input(self.SETTINGS["input_text_color"], key='_input_text_color_', pad=((8, 0), (0, 0)), size=(22, 1), visible=False), sg.Text('Input text color', visible=False)],
                [sg.B("Set theme", tooltip="This will reload the main window, values will be lost."), sg.B("Clear theme", visible=False)],
            ], title='Theme', relief=sg.RELIEF_SUNKEN)],
            [sg.B('Save', tooltip="Only saves the settings. To apply theme, please use 'Set theme' button"), sg.B("Test", visible=False),
             sg.B('Exit', key='_settings_exit_')]
        ]

        window = sg.Window('Settings', layout, modal=True, keep_on_top=True, finalize=True, return_keyboard_events=True,
                                        location=self.settings_window_location, size=self.settings_window_size)

        for key in self.SETTING_TO_ELEMENT_KEYS:  # update window with the values read from settings file
            try:
                window[self.SETTING_TO_ELEMENT_KEYS[key]].update(value=self.SETTINGS[key])
            except Exception as e:
                print(f'Problem updating PySimpleGUI window from settings. Key = {key}')


        self.settings_window = window
        return self.settings_window
# ---------------- END settings layout ---------------------- #

    def load_settings(self):
        try:
            with open(self.SETTINGS_FILE, 'r') as f:
                self.SETTINGS = jsonload(f)
        except Exception as e:
            sg.popup_quick_message(f'No settings file found... will create one for you', f'exception {e}',
                                   keep_on_top=True, background_color='red', text_color='white')
            self.SETTINGS = self.DEFAULT_SETTINGS
            self.save_settings(None)

    def save_settings(self, values):
        if values:  # if there are stuff specified by another window, fill in those values
            for key in self.SETTING_TO_ELEMENT_KEYS:  # update window with the values read from settings file
                try:
                    self.SETTINGS[key] = values[self.SETTING_TO_ELEMENT_KEYS[key]]
                except Exception as e:
                    print(f'Problem updating settings from window values. Key = {key}')

        with open(self.SETTINGS_FILE, 'w') as f:
            jsondump(self.SETTINGS, f)
        if self.event is not None:
            if self.event == "Set theme":
                string = "Reloading"
            else:
                string = "Settings saved"
            x = self.main_window_center[0]
            y = self.main_window_center[1]
            if x is not None and y is not None:
                coords = (x-50, y+100)
            else:
                coords = (x, y)

            sg.popup_no_buttons(string, keep_on_top=True,
                                                  auto_close=True,
                                                  auto_close_duration=1,
                                                  non_blocking=False,
                                                  no_titlebar=True,
                                                  location=coords)

# ---------------- END settings methods --------------------- #
    def color_validator(self, color):
        widget = tkinter.Tk()
        try:
            widget.winfo_rgb(color)
            widget.destroy()
            return True
        except:
            widget.destroy()
            return False

    def set_default_theme(self):
        s = self.SETTINGS
        sg.theme(s["theme"])

    def clear_theme(self):
        s = self.SETTINGS
        for key, color in s.items():
            if "color" in key:
                s[key] = ""
                self.settings_window[self.SETTING_TO_ELEMENT_KEYS[key]].update(value="")
        sg.theme(s['theme'])

    def set_theme(self, clear=False):
        s = self.SETTINGS
        sg.theme(s['theme'])

        for key, color in s.items():
            if "color" in key:
                if not self.color_validator(color) and color != "":
                    s[key] = ""
                    print(f"'{key}' - '{color}' is not valid color. Set to blank.")
        print(sg.theme_background_color())
        color = s["bkgrnd_color"] if s["bkgrnd_color"] != "" else sg.theme_background_color()
        sg.theme_background_color(color=color)
        sg.theme_element_background_color(color=color)
        sg.theme_text_element_background_color(color=color)
        print(sg.theme_background_color())

        b_text_color = s["button_text_color"] if s["button_text_color"] != "" else sg.theme_button_color()[0]
        color = s["button_color"] if s["button_color"] != "" else sg.theme_button_color()[1]
        sg.theme_button_color(color=(b_text_color, color))

        color = s["text_color"] if s["text_color"] != "" else sg.theme_text_color()
        sg.theme_text_color(color=color)
        sg.theme_element_text_color(color=color)

        color = s["input_text_color"] if s["input_text_color"] != "" else sg.theme_input_text_color()
        sg.theme_input_text_color(color=color)

        color = s["input_color"] if s["input_color"] != "" else sg.theme_input_background_color()
        sg.theme_input_background_color(color=color)



    def cprint(self, string, text_color=None):
        if text_color is None:
            text_color = self.SETTINGS["out_text_color"]
        sg.cprint(string, text_color=text_color)
        self.main_window.refresh()

    def set_win_pos(self):
        self.main_window_location = self.main_window.CurrentLocation()
        self.main_window_size = self.main_window.Size
        x = self.main_window_location[0]
        y = self.main_window_location[1]
        main_size_x = self.main_window_size[0]
        main_size_y = self.main_window_size[1]

        """Sets x/y variables to to middle of main window. 
        Adjustment of sub-window coordinates will be below"""
        x = x + (main_size_x / 2)
        y = y + (main_size_y / 2)
        self.main_window_center = (x, y)

        size_x = self.settings_window_size[0]
        size_y = self.settings_window_size[1]
        """Divides settings window x/y size coord by two to find the center of the window.
           It then subtracts that for x/y (main window center) so that the middle of the 
           settings window is ontop of the middle of the main window."""
        self.settings_window_location = (x - (size_x / 2), y - (size_y / 2))
        self.config_popup_location = (x, y + 500)




