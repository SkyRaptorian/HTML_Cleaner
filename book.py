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
    # CLASS VARIABLES --------------------------------------------------------------------------------------------------
    # Technically not needed at the start for python, but easier to see here
    #file_types: dict = {
    #    FileType.LIBREOFFICE: "LibreOffice"
    #}

    origin_folder = ".." #The origin folder with all the chapter files
    chapter_file_name = "Chapter {}" #The naming convention of the chapter files
    #Dictionary of any additional chapter files that do not fit the standard chapter conventions in chapter_name
    #format: {file name: final file name}
    #folders are the same as defined of chapter_path and final_path
    additional_files =  {} #Dictionary of any additional files and their details

    book_title = "" #The title of the book, String
    chapter_format = "{}" #The format of the chapter numbering, String

    section_break_symbol = "###" #The value of the section break to be replaced, String
    need_section_break_replace = False #If a section break scan is needed, Bool

    style_dict = {} #All style replacements, Dictionary
    need_styling = False #Whether there is a need for styling

    # CONSTRUCTORS ############################################################################
    def __init__(self, file_version, json_file):
        """
        The init function.

        :param int file_version: A file version to compare against
        :param file json_file: The JSON file to parse
        """
        self.version: int = file_version  # The version in order to check for compatibility issues
        self.type: str = None  # Where the html files where generated, LibreOffice as default

        self.rules: dict = {}  # A dictionary with all the specific rules for each book. AKA no_links and such

        try:
            self.read_format(json_file)  # Get information from JSON file
        except KeyError as error:
            print("The provided JSON file is missing the value: " + str(error))
            exit()
        except:
            print("There is an error with the JSON file provided.")
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
        if "file_type" in format_dict and format_dict["file_type"] in FileType:
            # If there is a file_type in file AND if it is a valid (found in enum)
            self.type = format_dict["file_type"]
        else:
            print("No valid file_type provided.")
            exit()

        # GET FILE PATHS
        match self.type:
            case FileType.LIBREOFFICE:
                self.origin_folder = format_dict["origin_folder"]
                self.chapter_file_name = format_dict["chapter_files"]
                self.additional_files = format_dict["additional_files"]
            case FileType.AO3:
                self.main_file = format_dict["main_file"]

                # AO3 RULES
                self.rules["oneshot"] = format_dict["oneshot"]
                self.rules["no-links"] = format_dict["no-links"]
            case FileType.SERIES:
                pass

        # BASIC INFO ---------------------------------------------------------------------------
        self.book_title = format_dict["title"]
        self.chapter_format = format_dict["chapter_format"]

        #SECTION BREAK -------------------------------------------------------------------------
        if "sectionbreak_symbol" in format_dict:
            self.section_break_symbol = format_dict["sectionbreak_symbol"]
            self.need_section_break_replace = True

        #STYLES --------------------------------------------------------------------------------
        if "style_rules" in format_dict:
            self.style_dict = format_dict["style_rules"]
            self.need_styling = True
    
        return self

    #TODO: Move format_reader to constructor
    # PYTHON CLASS METHODS ####################################################################
    def __str__(self):
        output = "Book File:\n"
        output += "\tVersion: " + str(self.version) + "\n" 
        output += "\tType: " + self.type + "\n\n" 
        output += "\tOrigin Folder: " + self.origin_folder + "\n"
        output += "\tChapter File Name: " + self.chapter_file_name + "\n"
        output += "\tAdditional Files: " + str(self.additional_files) + "\n"
        output += "\tBook Title: " + self.book_title + "\n" 
        output += "\tChapter Format: " + self.chapter_format + "\n" 
        output += "\tSection Break:\n"
        output += "\t\tSymbol: " + self.section_break_symbol + "\n"
        output += "\t\tScan?: " + str(self.need_section_break_replace) + "\n"
        output += "\tStyles:\n"
        output += "\t\t" + str(self.style_dict) + "\n"
        output += "\t\tAdd Styles?: " + str(self.need_styling) + "\n"

        return output