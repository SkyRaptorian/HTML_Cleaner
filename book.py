"""
Manages all information about processed book including file paths and formatting rules
"""

# IMPORTS ##############################################################################################################
import json
import enum


# ENUM #################################################################################################################
class FileType(str, enum.Enum):
    """
    An enum to contain all valid file types.

    Inherits from string to assist in comparisons
    """
    LIBREOFFICE = "LibreOffice"
    AO3 = "ao3"
    SERIES = "Series"


# MAIN CLASS ###########################################################################################################
class Book:
    """
    Class to contain information about the book being processed.
    """
    # CONSTRUCTORS #####################################################################################################
    def __init__(self, file_version, json_file):
        """
        The init function.

        :param int file_version: A file version to compare against
        :param file json_file: The JSON file to parse
        """
        self.version: int = file_version  # The version in order to check for compatibility issues
        self.type: str | None = None  # Where the html files where generated, LibreOffice as default

        self.primary_path: str | None = None  # The main path of the book,
        # LibreOffice - main folder, ao3 - single file
        self.additional_paths: dict = {}  # A dict of any additional paths
        self.file_name: str | None = None  # The file naming convention for numbered parts

        self.title: str | None = None  # The title of the book
        self.chapter_title: str | None = None  # The title of the chapters. Will be formatted

        self.rules: dict = {}  # A dictionary with all the specific rules for each book. AKA no_links and such
        self.styles: dict = {}  # All style replacements

        try:
            self.read_format(json_file)  # Get information from JSON file
        except KeyError as error:
            print("The provided JSON file is missing the value: " + str(error))
            exit()
        except Exception as error:
            print("There is an error with the JSON file provided.")
            print("Error: " + str(error))
            exit()

    def read_format(self, file):
        """
        Read the JSON file into the class. Called from __init__

        :param file file: A JSON file to parse
        :return: Void
        """
        # SET UP -------------------------------------------------------------------------------------------------------
        format_dict: dict = json.load(file)  # Load JSON fil

        # Check file version matches
        if format_dict["version"] != self.version:
            print("The JSON file has a different version then the program provided.")
            exit()

        # BUILD BOOK FORMAT --------------------------------------------------------------------------------------------
        # FILE TYPE
        if format_dict["file_type"] in FileType:
            # If there is a file_type in file AND if it is a valid (found in enum)
            self.type = format_dict["file_type"]
        else:
            print("No valid file_type provided.")
            exit()

        # GET FILE PATHS
        match self.type:
            case FileType.LIBREOFFICE:
                self.primary_path = format_dict["origin_folder"]
                self.additional_paths = format_dict["additional_files"]

                self.file_name = format_dict["chapter_files"]
            case FileType.AO3:
                self.primary_path = format_dict["main_file"]

                # AO3 RULES
                self.rules["oneshot"] = format_dict["oneshot"]
                self.rules["no-links"] = format_dict["no-links"]
            case FileType.SERIES:
                pass

        # BASIC INFO ---------------------------------------------------------------------------
        self.title = format_dict["title"]
        self.chapter_title = format_dict["chapter_format"]

        # SECTION BREAK -------------------------------------------------------------------------
        if "sectionbreak_symbol" in format_dict:
            self.rules["sectionbreak"] = format_dict["sectionbreak_symbol"]

        # STYLES --------------------------------------------------------------------------------
        if "style_rules" in format_dict:
            self.styles = format_dict["style_rules"]
    
        return self

    # PYTHON CLASS METHODS ####################################################################
    # TODO: UPDATE METHOD
    def __str__(self):
        output = "Book File:\n"
        output += "\tVersion: " + str(self.version) + "\n" 
        output += "\tType: " + self.type + "\n\n" 
        output += "\tPrimary Path: " + self.primary_path + "\n"
        output += "\tChapter File Name: " + self.file_name + "\n"
        output += "\tAdditional Files: " + str(self.additional_paths) + "\n"
        output += "\tBook Title: " + self.title + "\n"
        output += "\tChapter Format: " + self.chapter_title + "\n"
        output += "\tSection Break:\n"
        output += "\t\tSymbol: " + self.rules["sectionbreak"] + "\n"
        output += "\tStyles:\n"
        output += "\t\t" + str(self.styles) + "\n"

        return output
