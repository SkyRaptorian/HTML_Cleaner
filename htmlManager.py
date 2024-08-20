from bs4 import BeautifulSoup
from bs4 import Comment

import re  #Needed for string searches

#Namespace dictionary, Manages all namespaces for consistency
namespace_dict = {
    "xmlns": "http://www.w3.org/1999/xhtml",
    "xmlns:epub": "http://www.idpf.org/2007/ops"
}

#ARGUMENT SPACE
#vars that cover cmd line arguments to take in top level

NO_LINKS = False


def clean_html_libreOffice(soup, book, count):
    # INITIAL HTML SET UP ###################################################################################
    # NAMESPACES --------------------------------------------------------------------------------------------
    #ADD XHTML NAMESPACE
    soup.html["xmlns"] = namespace_dict["xmlns"]
    #ADD EPUB TYPE NAME SPACE
    soup.html["xmlns:epub"] = namespace_dict["xmlns:epub"]

    # MANAGE HTML HEAD --------------------------------------------------------------------------------------
    #MANAGE HEAD TAGS
    soup.title.string = book.book_title + " | " + book.chapter_format.format(count)  #Populate <title> tags

    #REMOVE LibreOffice META TAGS
    soup.find("meta", attrs={"name": "generator"}).decompose()
    soup.find("meta", attrs={"name": "created"}).decompose()
    soup.find("meta", attrs={"name": "changed"}).decompose()

    #REMOVE DEFAULT STYLING
    soup.find("style").decompose()

    #MANAGE HTML BODY ---------------------------------------------------------------------------------------
    #REMOVE AUTO GENERATED BODY TAG ATTRIBUTES
    attr_to_del = soup.body.attrs.copy()  #Copy dictionary to prevent iteration issues
    for attr in attr_to_del:
        del soup.body[attr]  # Delete all attributes in the body tag

    #WRAP BODY TEXT IN SECTION TAG FOR ACCESSIBILITY
    #JANKY JANK... there is probably easier way to wrap everything in the body within a section, but this works too
    #TODO: Find the better method
    soup.body.wrap(soup.new_tag("section"))
    soup.section.body.unwrap()
    soup.section.wrap(soup.new_tag("body"))

    #ADD ACCESSABILITY ROLES
    soup.body.section["epub:type"] = "chapter"
    soup.body.section["role"] = "doc-chapter"

    # HTML STYLING FROM DICTIONARY #########################################################################
    #START STYLES FROM FORMAT DICTIONARY
    #add dictionary styles
    for tag_type in book.style_dict:
        #configure tags to be searchable, change style class, clear all attributes.
        for styled_tag in soup.find_all(tag_type):
            styled_tag["class"] = book.style_dict[tag_type]

    # ADD SECTION BREAKS
    # MUST BE HR FOR ACCESSABILITY - ANY IMAGES MUST BE DONE IN CSS AS BACKGROUND IMAGE
    for l in soup.find_all("p", string=book.section_break_symbol):
        #Create hr tag
        linebreak_tag = soup.new_tag("hr")
        #add css file
        linebreak_tag["class"] = "linebreak"

        #replace placeholder symbol with new tag
        l.replace_with(linebreak_tag)

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


# A function to clean a generated html file from Archive of Our Own (https://archiveofourown.org/)
# Must be locally downloaded and path provided into. Splits file into multiple xhtml files.
# Called once
def clean_html_ao3(main_soup, format_book):
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

    # START CHAPTERS
    chapter_contents = main_soup.find("div", id="chapters").find_all("div", class_="userstuff")  #Get all chapter text

    # loop through all chpater contets
    for chapter_text in chapter_contents:
        soup = build_chapter(chapter_text, "ao3")
        # If there is no soup then build failed, skipped
        if (not soup):
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


def build_chapter(file_soup, formatype) -> BeautifulSoup:
    """
    ARGS:
    file_soup: BeautifulSoup
        Soup made from file. The file to be cleaned
    formatype: String
        The type of file (where the file was generated). Controls logic paths for clean up.
        NOT IMPLEMENTED: ASSUMES ao3
    """
    #BUILD SKELETON FILE ------------------------------------------------------------------------------------
    epub_roles = {"epub:type": "chapter", "role": "doc-chapter"}
    soup = create_base_xhtml(epub_roles, "Chapter")  #Placeholder title until later search
    soup.section["class"] = "chapter-text"  #add chapter css class

    # GET CHAPTER NOTES -------------------------------------------------------------------------------------
    front_note = file_soup.find_previous_sibling("div", class_="meta group")  #Get possible front meta-group
    end_note = file_soup.find_next_sibling()  #get possible endnote - have to check its an endnote

    # START CHAPTER PARSE -----------------------------------------------------------------------------------
    if (not front_note):  #If there isn't a front note possible sub chapter - ignore
        return None  #Return empty to be able to check if succeed

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


def build_afterword(file_soup, format_type) -> BeautifulSoup:
    # CREATE BASIC FILES
    epub_roles = {"epub:type": "preface", "role": "doc-preface"}
    soup = create_base_xhtml(epub_roles, "Afterword")
    # ADD CONTENT
    create_summary("End Notes:", file_soup.find("blockquote"), soup.find("section"))

    return soup

# HELPER FUNCTIONS ##########################################################################################
#############################################################################################################


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
    output = open(file_name, "w")  #Create file
    soup.encode(formatter="html")  #encode to html
    output.write(str(soup))  #Write to file


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


#Check every for every disallowed attributes and clear them
def remove_dissallowed_atrributes(soup):
    #ALIGN -------------------------------------------------
    attr_search = soup.find_all(align=True)
    for tag in attr_search:
        del tag["align"]  #Remove align tag
