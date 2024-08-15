#A class to read a json file and retrive the formatting rules of the book

import json #The JSON parser for python

import book #custom class

#Take a json file with defined formats and return a book object with those settings stored
def readFormat(file) -> book:
    # SET UP ###############################################################################################
    #Parse from JSON:
    format_dict = json.load(file)

    #check file version
    #if different fail out and end program
    #TODO:
    new_book = book.book(format_dict["version"]) #Create new book

    # BUILD BOOK FORMAT ###################################################################################
    
    # GET FILE TYPE
    #TODO:

    # BASIC INFO ------------------------------------------------------------------------------------------
    new_book.book_title = format_dict["title"]
    new_book.chapter_format = format_dict["chapter_format"]

    #SECTION BREAK ----------------------------------------------------------------------------------------
    if "sectionbreak_symbol" in format_dict:
        new_book.section_break_symbol = format_dict["sectionbreak_symbol"]
        new_book.need_section_break_replace = True
    
    #STYLES -----------------------------------------------------------------------------------------------
    if "style_rules" in format_dict:
        new_book.style_dict = format_dict["style_rules"]
        new_book.need_styling = True
    
    print(new_book)
    return new_book
