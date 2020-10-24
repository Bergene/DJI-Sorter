from core.file_handler import FileHandler
from core.gui import Gui
import PySimpleGUI as sg
from pprint import pprint


def main():
    gui = Gui()
    fh = FileHandler()

    # gui.create_main_window()  # Must be here for popup coordinates
    # gui.set_win_pos()  # Must be here for popup coordinates
    # gui.main_window.close()  # Must be here for popup coordinates
    gui.load_settings()
    gui.create_main_window()
    while True:  # Event Loop
        s = gui.SETTINGS
        window, event, values = sg.read_all_windows()
        gui.values = values
        gui.event = event
        sg.cprint_set_output_destination(window, "_ML_")
        fh.cp = gui.cprint
        print("_"*50)
        print(f"Window: {'Main_window' if window == gui.main_window else 'Settings_window'}")
        print(f"Event: {event}")

        if window == gui.main_window:
            if window == sg.WIN_CLOSED or event in (None, "_main_exit_"):  # if all windows were closed
                break
            else:
                gui.set_win_pos()  # Error will occur if trying to set coordinates on a closed window, hence this will only be called if a window is not closed.

                if event in ("Properties", "Settings"):
                    if not gui.settings_window:
                        gui.create_settings_window()
                        # gui.update_theme_input(values)

                elif event == "Show Files":
                    formats = gui.get_chkbox_val(values)  # Gets a list of formats depending on which checkboxes are checked
                    fh.get_files_(path=values["_input_"], formats=formats, recursive=values['_SUB_CB_'], settings=s)

                elif event == "Move":
                    if fh.files_list is None:
                        gui.cprint("Files list is empty")
                        formats = gui.get_chkbox_val(values)  # Gets a list of formats depending on which checkboxes are checked
                        fh.get_files_(path=values["_input_"], formats=formats, recursive=values['_SUB_CB_'], settings=s)
                    fh.move(path_to=values["_output_"],
                            copy=s['C_Radio'],
                            output_silent=(not s['Moved']),
                            transfer_dialog=(not s['Silent']),
                            testrun=s['Testrun'])
                    if not s['Testrun'] and values['_AUTHOR_CB_']:
                        """This should not run if it is a test run.
                           As no files will be moved/copied during 
                           a test run, there will be no files to 
                           an author to. This can cause errors.
                           """
                        fh.add_author(duplicate=s['Duplicate'],
                                      author=values["_author_in_"],
                                      output_silent=(not s['AuthorOutput']))

                elif event == "Test":
                    print(f"Path to: {values['_output_']}\n ")
                    print("\n\nValues\n")
                    for key, value in values.items():
                        print(f"Key: {key} - Value: {value}")
                    print("\n\nSettings\n")
                    for key, value in s.items():
                        print(f"Key: {key} - Value: {value}")
                elif event == "Clear":
                    window["_ML_"].update(value="")

                elif event == "_AUTHOR_CB_":
                        window.FindElement('_author_in_').Update(disabled=(not values["_AUTHOR_CB_"]))  # Assigned True/False from CB value

                elif event in ('_SUB_CB_', '_DNG_CB_', '_MOV_CB_', '_JPG_CB_', '_input_'):
                    fh.files_list = None  # This is to prevent "Move" action from using an outdated files list after f.ex 'Recurse' has been turned on
                    print(f"Files list cleared.")

        elif window == gui.settings_window:
            gui.set_win_pos()
            if __name__ == '__main__':
                if event == sg.WIN_CLOSED or event in ('Exit', '_settings_exit_', None, 'Escape:27'):
                    window.close()
                    gui.settings_window = None

                elif event == 'Save':
                    gui.save_settings(values)
                    window.close()
                    gui.settings_window = None
                    fh.files_list = None  # This is to prevent "Move" action from using an outdated files list after f.ex 'Recurse' has been turned on

                elif event == "Set theme":
                    gui.save_settings(values)
                    gui.set_default_theme()
                    gui.main_window.close()
                    gui.settings_window.close()
                    gui.create_main_window()
                    gui.create_settings_window()
                    fh.files_list = None  # This is to prevent "Move" action from using an outdated files list after f.ex 'Recurse' has been turned on

                elif event == "Clear theme":
                    gui.clear_theme()
                    event, values = gui.settings_window.read(timeout=1)
                    gui.save_settings(values)
                    print("\n\nSettings\n")
                    for key, value in s.items():
                        print(f"Key: {key} - Value: {value}")

                    gui.main_window.close()
                    gui.settings_window.close()

                    print("\n\nSettings\n")
                    for key, value in s.items():
                        print(f"Key: {key} - Value: {value}")

                    gui.create_main_window()
                    gui.create_settings_window()

                    print("\n\nSettings\n")
                    for key, value in s.items():
                        print(f"Key: {key} - Value: {value}")

                elif event == "Test":
                    print("\n\nValues\n")
                    for key, value in values.items():
                        print(f"Key: {key} - Value: {value}")
                    print("\n\nSettings\n")
                    for key, value in s.items():
                        print(f"Key: {key} - Value: {value}")



                    fh.files_list = None  # This is to prevent "Move" action from using an outdated files list after f.ex 'Recurse' has been turned on

        print("\nEnd of loop\n")


if __name__ == '__main__':
    main()