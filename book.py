### Class to manage the details of the ebook for parameter passing
### AUTHOR: SkyRaptorian
### CREATION DATE: 11 AUG 2023
### MODIFIED DATE: 11 AUG 2023

import json #The JSON parser for python

class book:
    # CLASS VARIABLES #########################################################################
    #Technically not needed at the start for python, but easier to see here
    version = 0 #The version in order to check for compatability issues, int
    type = "LibreOffice" #Where the html files where generated, LibreOffice as defualt, String

    origin_folder = ".." #The origin folder with all the chapter files
    chapter_file_name =  "Chapter {}" #The naming convention of the chapter files
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
        self.version = file_version
        self.read_format(json_file)

    #Construct directly from json files
    def read_format(self, file):
        # SET UP ------------------------------------------------------------------------------
        #Parse from JSON:
        format_dict = json.load(file)

        #check file version
        #if different warn user and attempt to continue
        if format_dict["version"] != self.version:
            print("The JSON file has a different version then the program provided.\nAttempting to continue... problems may occur.\n")

        # BUILD BOOK FORMAT --------------------------------------------------------------------
    
        # GET FILE TYPE
        self.type = format_dict["file_type"]

        # GET FILE PATHS
        self.origin_folder = format_dict["origin_folder"]
        self.chapter_file_name =  format_dict["chapter_files"]
        self.additional_files =  format_dict["additional_files"]

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