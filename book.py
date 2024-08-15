### Class to manage the details of the ebook for parameter passing
### AUTHOR: SkyRaptorian
### CREATION DATE: 11 AUG 2023
### MODIFIED DATE: 11 AUG 2023

import json #The JSON parser for python

class book:
    # CLASS VARIABLES #########################################################################
    version = 0 #The version in order to check for compatability issues, int
    type = "LibreOffice" #Where the html files where generated, LibreOffice as defualt, String

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
        #TODO:

        # BUILD BOOK FORMAT --------------------------------------------------------------------
    
        # GET FILE TYPE
        #TODO:

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
        output += "\tBook Title: " + self.book_title + "\n" 
        output += "\tChapter Format: " + self.chapter_format + "\n" 
        output += "\tSection Break:\n"
        output += "\t\tSymbol: " + self.section_break_symbol + "\n"
        output += "\t\tScan?: " + str(self.need_section_break_replace) + "\n\n"
        output += "\tStyles:\n"
        output += "\t\t" + str(self.style_dict) + "\n"
        output += "\t\tAdd Styles?: " + str(self.need_styling) + "\n"

        return output