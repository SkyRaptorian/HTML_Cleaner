from bs4 import BeautifulSoup
from bs4 import Comment

import os

import re  #Needed for string searches

#Namespace dictionary, Manages all namespaces for consistency
namespace_dict = {
    "xmlns": "http://www.w3.org/1999/xhtml",
    "xmlns:epub": "http://www.idpf.org/2007/ops"
}

# ARGUMENT SPACE
# vars that cover cmd line arguments to take in top level

# BOOK RULES
NO_LINKS: bool = False
ONESHOT: bool = False

# ENTRANCE FUNCTION ####################################################################################################
########################################################################################################################


# The main entrance function, takes a book and produces clean files.
#Sets book-wide variables and go to correct function
def clean_html(book):
    match book.type:
        case "LibreOffice":
            # BUILD CHAPTER PATH
            chapter_count = 1
            chapter_path = "{}/{}.html".format(book.origin_folder, book.chapter_file_name)
            #print(chapter_path)
            # LOOP THROUGH ALL CHAPTERS
            while os.path.exists(chapter_path.format(chapter_count)):
                #print(chapter_path.format(chapter_count))
                file = open(chapter_path.format(chapter_count), "r")
                file_soup = BeautifulSoup(file, "html.parser")

                single_file_libreOffice(file_soup, book, chapter_count)

                file.close()

                chapter_count += 1
        case "ao3":
            # SET LOGIC VARIABLES
            global NO_LINKS
            global ONESHOT

            NO_LINKS = book.no_links
            ONESHOT = book.oneshot

            # OPEN FILES
            file = open(book.main_file+".html", "r")
            file_soup = BeautifulSoup(file, "html.parser")

            single_file_ao3(file_soup, book)

            file.close()


# BOOK FORMAT LOGIC ####################################################################################################
########################################################################################################################

def single_file_libreOffice(file_soup, book, count):
    # INITIAL HTML SET UP ----------------------------------------------------------------------------------------------
    chapter_title = book.book_title + " | " + book.chapter_format.format(count)
    epub_roles = {"epub:type": "chapter", "role": "doc-chapter"}
    soup = create_base_xhtml(epub_roles, chapter_title)

    # MANAGE CONTENTS --------------------------------------------------------------------------------------------------
    soup.section.append(file_soup.body)
    soup.section.body.unwrap()  # Remove additional body tag

    # MANAGE STYLING ---------------------------------------------------------------------------------------------------
    # add dictionary styles
    for tag_type in book.style_dict:
        # configure tags to be searchable, change style class, clear all attributes.
        for styled_tag in soup.find_all(tag_type):
            styled_tag["class"] = book.style_dict[tag_type]

    # ADD SECTION BREAKS
    # MUST BE HR FOR ACCESSABILITY - ANY IMAGES MUST BE DONE IN CSS AS BACKGROUND IMAGE
    for linebreak in soup.find_all("p", string=book.section_break_symbol):
        # Create hr tag
        linebreak_tag = soup.new_tag("hr")
        # add css file
        linebreak_tag["class"] = "linebreak"

        # replace placeholder symbol with new tag
        linebreak.replace_with(linebreak_tag)

    #REMOVE JUNK TO SIMPLIFY -------------------------------------------------------------------
    #LibreOffice adds these tags for small things that don't always make sense. Especially with
    #cut and paste. Add manually after cleaning if specific effect needed.
    for data in soup.find_all("font"):
        data.unwrap()

    for data in soup.find_all("span"):
        data.unwrap()

    for data in soup.find_all(string="&nbsp;"):
        data.decompose()

    #ADDITIONAL ADJUSTMENTS --------------------------------------------------------------------
    #Add other things here - POV image adjustments
    for l in soup.find_all("pre"):
        comment = Comment(l.string)

        l.replace_with(comment)

    soup_to_file(soup, "final/" + str(count) + "-chapter.xhtml")


# A function to clean a generated html file from Archive of Our Own (https://archiveofourown.org/)
# Must be locally downloaded and path provided into. Splits file into multiple xhtml files.
# Called once
def single_file_ao3(main_soup, format_book):
    """
    ARGS:
        main_soup: the soup generated from the main html file
        format_book: the book class that holds the information of the book and format data
    """
    # CREATE FILES -----------------------------------------------------------------------------------------------------
    part_count = 0  #counter for the chapter - used for naming files

    # CREATE FOREWORD/PREFACE
    soup = build_preface(main_soup, "ao3")
    soup_to_file(soup, "final/" + str(part_count) + "-preface.xhtml")
    part_count += 1

    # CHAPTERS ---------------------------------------------------------------------------------------------------------
    if ONESHOT:
        # ONESHOT ONLY HAS ONE CHAPTER
        chapter_contents = main_soup.find("div", id="chapters").find("div",class_="userstuff")  # Get Text
        soup = build_oneshot(chapter_contents, "ao3")

        soup_to_file(soup, "final/" + str(part_count) + "-chapter.xhtml")
        part_count += 1
    else:
        # IF NOT ONESHOT HAS MULTIPLE CHAPTERS
        chapter_contents = main_soup.find("div", id="chapters").find_all("div", class_="userstuff")  # Get Chapters
        # loop through all chapter contents
        for chapter_text in chapter_contents:
            soup = build_chapter(chapter_text, "ao3")
            # If there is no soup then build failed, skipped
            if not soup:
                continue

            soup_to_file(soup, "final/" + str(part_count) + "-chapter.xhtml")
            part_count += 1

    # AFTERWORD --------------------------------------------------------------------------------------------------------
    afterword_search = main_soup.find("div", id="afterword").find("div", id="endnotes")  # Look for a valid afterword
    if afterword_search:  # If there is an afterword
        soup = build_afterword(afterword_search, "ao3")
        soup_to_file(soup, "final/" + str(part_count) + "-afterword.xhtml")


# FILE PART MANAGEMENT FUNCTIONS #######################################################################################
########################################################################################################################

# Pulls a preface from a soup
def build_preface(file_soup, formatype) -> BeautifulSoup:
    """
    ARGS:
    file_soup: BeautifulSoup
        Soup made from file. The file to be cleaned
    formatype: String
        The type of file (where the file was generated). Controls logic paths for clean up.
        NOT IMPLEMENTED: ASSUMES ao3
    """
    #BUILD SKELETON FILE -------------------------------------------------------------------------------------
    epub_roles = {"epub:type": "preface", "role": "doc-preface"}
    soup = create_base_xhtml(epub_roles, "Preface")  #Basic File

    soup.section.append(soup.new_tag("h1", attrs={"class": "title"}))  #Heading
    soup.section.append(soup.new_tag("p", attrs={"class": "byline"}))  #Author byline
    soup.section.append(soup.new_tag("p", attrs={"class": "link"}))  #Archive of Our Own link

    soup.section.append(soup.new_tag("div", attrs={"class": "work-tags"}))  #Div for work tags
    soup.div.append(soup.new_tag("dl"))  #Start description list

    soup.section.append(soup.new_tag("div", attrs={"class": "summary"}))  #Div for work summary

    #ENTER BASIC DETAILS ------------------------------------------------------------------------------------
    # HEADING
    soup.h1.string = file_soup.find("h1").string

    # AUTHOR
    soup.find("p", class_="byline").string = "by "  #Start string
    soup.find("p", class_="byline").append(
        set_link(file_soup.find("div", class_="byline").a))  #Append author name to byline after checking links

    # WORK LINK
    work_link = file_soup.find("p", class_="message").find_all("a")
    soup.find("p", class_="link").string = "Posted originally on the "  #Start the link line
    soup.find("p", class_="link").append(set_link(work_link[0]))  #Add first link - Archive of Our Own
    soup.find("p", class_="link").append(" at ")  #bridge links
    soup.find("p", class_="link").append(set_link(work_link[1]))  #Add specific work link
    soup.find("p", class_="link").append(".")  #end line

    # TAG LIST --------------------------------------------------------------------------------------------
    for tag in file_soup.dl:  #Get all description elements
        if (tag.name == "dt"):  #If description element title
            soup.dl.append(tag)
        if (tag.name == "dd"):  #If description element decription
            for a in tag.find_all("a"):
                old_tag = a.replace_with(set_link(a))  #Check all links in dd
            soup.dl.append(tag)

    # SUMMARY AND NOTES ----------------------------------------------------------------------------------
    # SUMMARY, ALL WORKS HAVE ONE
    summary_text = file_soup.find("div", id="preface").find("p",
                                                            string="Summary").find_next_sibling()  #Get the summary blocktext
    create_summary("Summary", summary_text, soup.find("div", class_="summary"))

    # NOTES, NEED TO CHECK FIRST
    notes_text = file_soup.find("div", id="preface").find("p",
                                                          string="Notes").find_next_sibling()  #Get the notes blocktext

    if (notes_text):  #Check there is a note
        soup.section.append(soup.new_tag("div", attrs={"class": "notes"}))  #create div for work notes
        create_summary("Notes", notes_text, soup.find("div", class_="notes"))  #MAke the note text

    return soup


def build_oneshot(file_soup, formatype) -> BeautifulSoup:
    """
        ARGS:
        file_soup: BeautifulSoup
            Soup made from file. The file to be cleaned
        formatype: String
            The type of file (where the file was generated). Controls logic paths for clean up.
            NOT IMPLEMENTED: ASSUMES ao3
        """
    # BUILD SKELETON FILE ----------------------------------------------------------------------------------------------
    epub_roles = {"epub:type": "chapter", "role": "doc-chapter"}
    soup = create_base_xhtml(epub_roles, "Chapter")  # Placeholder title until later search
    soup.section["class"] = "chapter-text"  # add chapter css class

    # ADD CONTENT ------------------------------------------------------------------------------------------------------
    # TITLE
    front_note = file_soup.find_previous_sibling()  # Get Title
    soup.section.append(soup.new_tag("h1"))
    soup.h1.string = front_note.string
    soup.title.string = front_note.string

    # CHAPTER
    file_soup["class"] = "body-text"  # Set css class
    soup.section.append(file_soup)

    return soup


def build_chapter(file_soup, formatype) -> BeautifulSoup:
    """
    ARGS:
    file_soup: BeautifulSoup
        Soup made from file. The file to be cleaned
    formatype: String
        The type of file (where the file was generated). Controls logic paths for clean up.
        NOT IMPLEMENTED: ASSUMES ao3
    """
    # BUILD SKELETON FILE ----------------------------------------------------------------------------------------------
    epub_roles = {"epub:type": "chapter", "role": "doc-chapter"}
    soup = create_base_xhtml(epub_roles, "Chapter")  #Placeholder title until later search
    soup.section["class"] = "chapter-text"  #add chapter css class

    # GET CHAPTER NOTES -------------------------------------------------------------------------------------
    front_note = file_soup.find_previous_sibling("div", class_="meta group")  #Get possible front meta-group
    end_note = file_soup.find_next_sibling()  #get possible endnote - have to check its an endnote

    # START CHAPTER PARSE -----------------------------------------------------------------------------------
    if not front_note:  # If there isn't a front note possible subchapter - ignore
        return None  # Return empty to be able to check if succeed

    # CREATE TITLE
    soup.section.append(soup.new_tag("h1"))  #Create title tag
    soup.h1.string = front_note.h2.string  #Get titles
    soup.title.string = front_note.h2.string

    # CHAPTER NOTES
    if (front_note.find("blockquote")):  #Check if their is a chapter summary/note
        #Create summary div
        soup.section.append(soup.new_tag("div", attrs={"class": "summary"}))
        #GET SUMMARY TEXT
        create_summary("Chapter Summary", front_note.find("blockquote"), soup.find("div", class_="summary"))

    # CHAPTER TEXT
    file_soup["class"] = "body-text"  #Set css class
    soup.section.append(file_soup)

    # CHAPTER END NOTES
    if (not end_note.h2):  #Only front notes have h2 tags, anything else is valid
        soup.section.append(soup.new_tag("div", attrs={"class": "endnotes"}))
        create_summary("Chapter End Notes", end_note.find("blockquote"), soup.find("div", class_="endnotes"))

    #ENSURE SOUP IS VALID
    remove_dissallowed_atrributes(soup)
    return soup


def build_afterword(afterword_text, format_type) -> BeautifulSoup:
    # CREATE BASIC FILES
    epub_roles = {"epub:type": "afterword", "role": "doc-afterword"}
    soup = create_base_xhtml(epub_roles, "Afterword")
    # ADD CONTENT
    soup.section.append(soup.new_tag("div", attrs={"class": "notes"}))  # Create a div for notes
    create_summary("End Notes:", afterword_text.blockquote, soup.div)

    return soup


# HELPER FUNCTIONS #####################################################################################################
########################################################################################################################

def create_base_xhtml(epub_roles, title) -> BeautifulSoup:
    #Creates an empty soup with the basic skeleton of a xhtml file created

    #CREATE NEW XHTML FILE ##################################################################################
    soup = BeautifulSoup("<!DOCTYPE html>", "html.parser")

    #CREATE SHELL -----------------------------------------------------
    soup.append(soup.new_tag("html"))  #Create html tag
    soup.html["xmlns"] = namespace_dict["xmlns"]
    soup.html["xmlns:epub"] = namespace_dict["xmlns:epub"]

    # CREATE HEAD -----------------------------------------------------
    soup.html.append(soup.new_tag("head"))  #Create head tag
    soup.html.head.append(soup.new_tag("meta"))  #Create meta tag
    soup.html.head.meta["charset"] = "utf-8"

    soup.html.head.append(soup.new_tag("title"))  #Create title tag, leave empty
    soup.find("title").string = title

    soup.html.head.append(
        soup.new_tag("link", attrs={"rel": "stylesheet", "type": "text/css", "href": "../styles.css"}))

    # CREATE BODY -----------------------------------------------------
    soup.html.append(soup.new_tag("body"))  #Create body tag
    soup.body.append(soup.new_tag("section"))  #Create section tag, needed for accessability roles
    #ADD ACCESSABILITY ROLES
    soup.body.section["epub:type"] = epub_roles["epub:type"]
    soup.body.section["role"] = epub_roles["role"]

    return soup


def soup_to_file(soup, file_name):
    # A function to save the soup to a file
    output = open(file_name, "w")   # Create file
    soup.encode(formatter="html")   # encode to html
    output.write(str(soup))   # Write to file

    print("COMPLETED: " + file_name + "                      ", end='\r')  # Add whitespace to keep clean


#return link based off of NO_LINKS rule
# if True replace a href tag with <i>
def set_link(tag):
    if (NO_LINKS):
        soup = BeautifulSoup("", "html.parser")  #Create a soup
        string_data = tag.string  #Get old tag string
        new_tag = soup.new_tag("i")  #Create new <i> tag
        new_tag.string = string_data  #give string to new tag
        return new_tag  #return new <i> tag
    else:
        return tag  #If NO_LINKS false - no changes needed


def create_summary(title, summary_text, summary_div):
    soup = BeautifulSoup("", "html.parser")  # Create a soup

    summary_div.append(soup.new_tag("h2"))  # Add a title
    summary_div.h2.string = title
    summary_div.append(summary_text)  # Add the text
    summary_div.blockquote.unwrap()  # Remove blockquote


# Check every for every disallowed attributes and clear them
def remove_dissallowed_atrributes(soup):
    # ALIGN
    attr_search = soup.find_all(align=True)
    for tag in attr_search:
        del tag["align"]  #Remove align tag
