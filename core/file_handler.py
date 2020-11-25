import re
import os
import ctypes
import winshell
from exiftool import ExifTool


class FileHandler:
    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0  # Returns 'True' if running as admin
    is_exif = (True if "exiftool.exe" in os.listdir(os.getcwd()) else False)  # Returns 'True' if exif in cwd

    def __init__(self):
        self.path_from = None  # Path where to search for files
        self.path_to = None  # Path where to move files to
        self.files_list = None
        self.cp = None

    def get_files(self, path_from=None, formats=None, recursive=False):
        if path_from is None or formats is None:  # If either variable is 'None' it will return the same
            return None
        else:
            print(formats)
            self.path_from = path_from
            results = os.listdir(path_from)  # Gets list of files and subdirs
            self.files_list = list()  # Creates empty list in 'files_list' variable
            for entry in results:
                path = os.path.join(path_from, entry)
                if not os.path.isdir(path):  # Only appends to 'files_list' if path is file
                    ext = FileHandler.get_ext(path)
                    if ext in formats:
                        self.files_list.append(path)
                if recursive:  # If recursion is enabled it walks through all subdirs and appends the file to 'files_list'
                    if os.path.isdir(path):
                        for root, dirs, files in os.walk(path, topdown=True):
                            for file in files:
                                path = os.path.join(root, file)
                                ext = FileHandler.get_ext(path)
                                if ext in formats:
                                    self.files_list.append(path)
            return self.files_list

    def get_dates(self):
        tag = "CreateDate"  # Metadata tag to extract from file
        exif_exe = os.path.join(os.getcwd(), "exiftool.exe")  # Path to 'exiftool.exe'
        exif = ExifTool()  # Initiate ExifTool instance
        exif.executable = exif_exe  # Set Exif exe location
        exif.start()  # Start Exif batch instance
        files_dt = list()  # Create empty list for which to append filepaths with creation date
        for file in self.files_list:
            date = exif.get_tag(tag, file).split(" ")[0].replace(":", "")  # Splits and formats the date tp the desirable format
            files_dt.append((date, file))
        exif.terminate()  # Terminates Exif instance after use
        self.files_list = files_dt
        return files_dt

    def sort(self):
        sorted = dict()  # Creates empty dictionary, used to sort files by date and format
        for date, file in self.files_list:
            ext = FileHandler.get_ext(file)
            sorted.setdefault(date, dict())
            sorted[date].setdefault(ext, list())
            sorted[date][ext].append(file)

        for date, ext_dict in sorted.items():  # This loops is used only to delete empty 'ext' list from 'sorted' dict
            delete = []
            for ext in ext_dict:
                if len(ext_dict[ext]) == 0:
                    delete.append(ext)
            for ext in delete:
                del ext_dict[ext]
        self.files_list = sorted

    def move(self, path_to=None, copy=True, output_silent=True, transfer_dialog=False, testrun=False):
        if path_to is not None:
            if not self.is_dir(directory=path_to, mkdir=True, chk_ptrn=True):
                self.cp("Bad path")
                return
            self.path_to = path_to
            new_path_files_list = list()  # Creates empty list to append new file path (used when adding author)
            if not output_silent and self.cp is not None:
                self.cp(f"{'Copying' if copy else 'Moving'} files from {self.path_from}")
            for date, ext_dict in self.files_list.items():
                date_folder = os.path.join(path_to, date)  # Creates path to date root folder
                self.is_dir(date_folder, mkdir=True)  # Checks if folder exists, if not it will be created
                for ext in ext_dict:
                    if ext != "JPG":  # JPG will be placed in date root folder
                        ext_folder = os.path.join(date_folder, ext)  # Creates path for 'ext' folder
                        self.is_dir(ext_folder, mkdir=True)  # Checks for folder and creates it if necessary
                    else:  # If 'ext' is JPG it will set 'ext_folder' to 'date_folder'
                        ext_folder = date_folder
                    for file in ext_dict[ext]:
                        if not output_silent and self.cp is not None:
                            file_ = file.split("\\")[-1]
                            self.cp(f"{'Copying' if copy else 'Moving'} {file_} to {ext_folder}")
                        new_path = os.path.join(ext_folder, file.split("\\")[-1])
                        duplicate_file = None
                        if not testrun:
                            if copy:
                                move_output = winshell.copy_file(file, ext_folder, allow_undo=True, no_confirm=False, rename_on_collision=True, silent=transfer_dialog)
                            else:
                                move_output = winshell.move_file(file, ext_folder, allow_undo=True, no_confirm=False, rename_on_collision=True, silent=transfer_dialog)
                            duplicate_file = move_output.get(new_path) #Checking 'move_output' for duplicate result
                        if duplicate_file is None:
                            new_path_files_list.append(new_path)
                        else:
                            new_path_files_list.append(duplicate_file)
                            if not output_silent and self.cp is not None:
                                duplicate_ = duplicate_file.split("\\")[-1]
                                self.cp(f"{' '*5}File is duplicate - New name: {duplicate_}")

            self.new_files_path = new_path_files_list

    def add_author(self, duplicate=False, author=None, output_silent=True):
        """Author should be applied to the files AFTER being moved
           to avoid writing anything to the SD card (it will make
           a duplicate of the file regardless, the 'duplicate'
           option only prevents the tool from deleting the original."""
        exif_exe = os.path.join(os.getcwd(), "exiftool.exe")
        exif = ExifTool()
        exif.executable = exif_exe
        exif.start()
        if not output_silent and self.cp is not None:
            self.cp(f"\nSetting author for files: {author}")
        for file in self.new_files_path:
            if not output_silent and self.cp is not None:
                file_ = file.split("\\")[-1]
                self.cp(f"Editing metadata for: {file_}")
            exif.execute(f"-Creator={author}".encode(), f"{'-overwrite_original' if not duplicate else ''}".encode(), file.encode())
        exif.terminate()

    def show_sorted_files(self):
        self.cp("Files found: ")
        for date, ext_files in self.files_list.items():
            self.cp(f"Creation date: {date}")
            for ext, files in ext_files.items():
                self.cp(f"{' '*5}File type: {ext}".rjust(5))
                for file in files:
                    self.cp(f"{' '*10}{file}")

    def count_sorted_files(self):
        counted = dict()
        string = "\nNumber of files:\n"
        for date in self.files_list.keys():
            for ext, files in self.files_list[date].items():
                counted.setdefault(ext, 0)
                counted[ext] += len(files)
        for ext, count in counted.items():
            string += f"{' '*5}{ext}: {count}\n"
        self.cp(string)

    def get_files_(self, path=None, formats=None, recursive=False, settings=None):
        """'cp' is gui.cprint method'."""
        if settings is None:
            settings = {"Files": True, "Dates": True, "Sorted": True, }
        if not self.is_dir(directory=path):
            self.cp("Bad path")
            return

        self.get_files(path_from=path, formats=(formats), recursive=recursive)  # Creates a list of files from 'fh.path_to'

        if settings["Files"] and self.cp is not None:
            self.cp("\n")
            for file in self.files_list:
                self.cp(file)
            self.cp(f"\nFound {len(self.files_list)} files.\n")

        self.get_dates()  # Gets the creation dates of the files
        if settings["Dates"] and self.cp is not None:
            self.cp("\n")
            for date, file in self.files_list:
                filename = file.split("\\")[-1]
                self.cp(f"Found date '{date}' for file '{filename}'")

        self.sort()  # Sorts the files
        if settings["Sorted"] and self.cp is not None:
            self.cp("\n")
            self.show_sorted_files()
            self.count_sorted_files()  # Counts files by format



    @classmethod
    def is_dir(cls, directory, mkdir=True, chk_ptrn=False):
        """Function to check if given dir exist. By default it creates the directory if it does not exist.
                  Args: 'directory' - Self explanatory
                        'mkdir - If 'True' it will create the directory if it does not exist
                        'chk_ptrn - If 'True' it will only check if the given path is a valid path format
                        """
        match = re.match(r'^[a-zA-Z]:\\(((?![<>:"/\\|?*]).)+((?<![ .])\\)?)*$',
                         directory)  # Check if given path is a valid path format
        if match:  # If 'directory' is a valid path
            if chk_ptrn:
                return True
            directory = match.group()  # Gets the validated path from the regex match
            if os.path.isdir(directory):  # Checks if directory exists on computer
                return True
            else:  # If it does not exist:
                if mkdir:  # If 'mkdir' is 'True' it will create the directory
                    os.makedirs(directory)
                    return True
                else:  # If 'mkdir' is 'False' it will return 'False' as the dir does not exist
                    return False
        else:  # If given path is not a valid path format it returns 'False'
            return False

    @classmethod
    def get_ext(cls, file):
        file_ext = os.path.splitext(file)
        file, ext = file_ext[0], file_ext[1].upper().replace(".", "")
        return ext