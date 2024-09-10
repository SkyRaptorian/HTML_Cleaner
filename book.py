"""
Contains data classes that manage information about the processed books
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


# FORMAT CLASS #########################################################################################################
class Format:
    """
    Class that manages all format data about a book.
    """
    # CONSTRUCTORS #####################################################################################################
    def __init__(self, file_version, json_file):
        """
        The init function.

        :param int file_version: A file version to compare against
        :param file json_file: The JSON file to parse
        """

        self.version: int = file_version
        """The version in order to check for compatibility issues"""
        self.type: str | None = None
        """What type of parser is needed."""

        self.primary_path: str | None = None
        """The primary file path to operate on. LibreOffice - main folder, ao3 - single file"""
        self.additional_paths: dict = {}
        """Dictionary of any additional path"""
        self.file_name: str | None = None
        """The string format for the file names. e.g. 'Chapter {}'"""

        self.title: str | None = None
        """The title of the book"""
        self.chapter_title: str | None = None
        """The title of the chapters. Will be formatted"""
        self.additional_info: dict = {}
        """Any additional info to be held about the files, mostly used by series"""

        self.rules: dict = {}
        """A dictionary with all the specific rules for each book. AKA no_links and such"""
        self.styles: dict = {}
        """All style replacements"""

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

                self.chapter_title = format_dict["chapter_format"]

                self.file_name = format_dict["chapter_files"]
            case FileType.AO3:
                self.primary_path = format_dict["main_file"]

                self.chapter_title = format_dict["chapter_format"]

                # AO3 RULES
                self.rules["oneshot"] = format_dict["oneshot"]
                self.rules["no-links"] = format_dict["no-links"]
            case FileType.SERIES:
                self.primary_path = format_dict["origin_folder"]
                self.additional_paths = format_dict["part_files"]

                self.additional_info["series_begun"] = format_dict["series_begun"]
                self.additional_info["series_updated"] = format_dict["series_updated"]
                self.additional_info["series_stats"] = format_dict["series_stats"]

                if not format_dict["series_description"] is None:
                    self.additional_info["series_description"] = format_dict["series_description"]
                if not format_dict["series_notes"] is None:
                    self.additional_info["series_notes"] = format_dict["series_notes"]

                # AO3 RULES
                self.rules["oneshot"] = format_dict["oneshot"]
                self.rules["no-links"] = format_dict["no-links"]

        # BASIC INFO ---------------------------------------------------------------------------
        self.title = format_dict["title"]

        # SECTION BREAK -------------------------------------------------------------------------
        if "sectionbreak_symbol" in format_dict:
            self.rules["sectionbreak"] = format_dict["sectionbreak_symbol"]

        # STYLES --------------------------------------------------------------------------------
        if "style_rules" in format_dict:
            self.styles = format_dict["style_rules"]
    
        return self

    # PYTHON CLASS METHODS ####################################################################
    def __str__(self):
        output = "Book File:\n"
        output += "\tVersion: " + str(self.version) + "\n" 
        output += "\tType: " + self.type + "\n"
        output += "\tBook Title: " + self.title + "\n\n"
        output += "\tPrimary Path: " + self.primary_path + "\n"
        output += "\tChapter File Name: " + self.file_name + "\n"
        output += "\tAdditional Files: " + str(self.additional_paths) + "\n"
        output += "\tRules:\n"
        output += "\t\t" + str(self.rules) + "\n"
        output += "\tStyles:\n"
        output += "\t\t" + str(self.styles) + "\n"

        return output


class BookPart:
    """
    Class that contains all the separate parts of a chapter to be sorted and assembled later.
    """
    def __init__(self, file_type: str):
        self.file_type: str = file_type
        """The type of file that the part comes from"""

        self.part_type: str = ""
        """The type of part for accessibility tags, e.g. chapter, preface"""

        self.path:str = ""
        """The final path that the file will be saved under"""

        self.part_soups: dict = {}
        """
        A dictionary that contains all separate soups that make up the different parts. Exclude section tags or large 
        wraps as they will be added in assembly.
        
        Will be assembled by the save to file function.
        
            * heading: The heading tag and contents
        
            * byline: Any byline or subheadings that make up a file
        
            * meta: Used in ao3 parsing to hold tag block
            
            * summary: Chapter summary or epigraph - keep as blockquote to assist in unwrap
            
            * start-notes: Any start notes of the chapter
        
            * main-text: The main text of the file/chapter 
            
            * end-notes: Any end notes of the chapter
        """

