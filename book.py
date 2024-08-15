### Class to manage the details of the ebook for parameter passing
### AUTHOR: SkyRaptorian
### CREATION DATE: 11 AUG 2023
### MODIFIED DATE: 11 AUG 2023

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
    def __init__(self, file_version):
        self.version = file_version

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
        output += "\t\tAdd Styles?: " + str(self.need_styling) 

        return output