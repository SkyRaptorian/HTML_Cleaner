"""
This module manages all the html functions.

Functions to clean the html and save the soup to file.

"""

# IMPORTS ##############################################################################################################
from bs4 import BeautifulSoup, NavigableString
from bs4 import Comment

from book import Format, BookPart

# GLOBAL VARIABLES #####################################################################################################
# Namespace dictionary, Manages all namespaces for consistency
namespace_dict = {
    "xmlns": "http://www.w3.org/1999/xhtml",
    "xmlns:epub": "http://www.idpf.org/2007/ops"
}

# Global book value for the module - None when nothing is provided
format_book: Format | None = None


# BOOK FORMAT LOGIC ####################################################################################################
########################################################################################################################

def clean_libreOffice(file_soup, file_book, count) -> BookPart:
    """
    The method to create valid xhtml from a provided soup generated from LibreOffice html

    Identify whether the file is a chapter or an additional file by looking at the variable type of count.
        * If int, chapter file
        * If str, additional file

    :param BeautifulSoup file_soup: The soup generated from the html file
    :param Format file_book: The book details object
    :param int|str count: The chapter number or the name of the additional file

    :return: A BookPart and a name that contains all information about the parsed file
    """
    # SET GLOBAL BOOK
    global format_book
    format_book = file_book

    chapter = BookPart(format_book.type)  # Create new book part with type

    # INITIAL HTML SET UP ----------------------------------------------------------------------------------------------
    epub_roles = {"epub:type": "chapter", "role": "doc-chapter"}

    soup = BeautifulSoup("", "html.parser")

    # GET PART TEXT ----------------------------------------------------------------------------------------------------
    soup.append(file_soup.body)
    soup.body.unwrap()  # Remove additional body tag

    # GET AND REMOVE HEADINGS
    heading_text = BeautifulSoup("", "html.parser")
    heading_text.append(soup.h1)  # Append removes the h1 from the soup
    chapter.part_soups["heading"] = heading_text

    # MANAGE STYLING ---------------------------------------------------------------------------------------------------
    # add dictionary styles
    for tag_type in file_book.styles:
        # configure tags to be searchable, change style class, clear all attributes.
        for styled_tag in soup.find_all(tag_type):
            styled_tag["class"] = file_book.styles[tag_type]

    # ADD SECTION BREAKS
    # MUST BE HR FOR ACCESSIBILITY - ANY IMAGES MUST BE DONE IN CSS AS BACKGROUND IMAGE
    for linebreak in soup.find_all("p", string=file_book.rules["sectionbreak"]):
        # Create hr tag
        linebreak_tag = soup.new_tag("hr")
        # add css file
        linebreak_tag["class"] = "linebreak"

        # replace placeholder symbol with new tag
        linebreak.replace_with(linebreak_tag)

    # REMOVE JUNK TO SIMPLIFY -------------------------------------------------------------------
    # LibreOffice adds these tags for small things that don't always make sense. Especially with
    # cut and paste. Add manually after cleaning if specific effect needed.
    final_clean(soup)

    # ADDITIONAL ADJUSTMENTS --------------------------------------------------------------------
    # Add other things here - POV image adjustments
    #for tag in soup.find_all("pre"):
        #comment = Comment(tag.string)

        #tag.replace_with(comment)

    chapter.part_soups["main-text"] = soup  # Add the full chapter text to the part

    return chapter


def clean_ao3(main_soup, file_book):
    """
    A function to clean a generated html file from Archive of Our Own (https://archiveofourown.org/)

    :param BeautifulSoup main_soup: The soup made from the generated html.
    :param Format file_book: The book details object
    :return: Void
    """
    # SET GLOBAL BOOK
    global format_book
    format_book = file_book

    # CREATE FILES -----------------------------------------------------------------------------------------------------
    part_count = 0  # counter for the chapter - used for naming files

    # CREATE FOREWORD/PREFACE
    soup = build_preface(main_soup, "ao3")

    final_clean(soup)

    soup_to_file(soup, "final/" + str(part_count) + "-preface.xhtml")
    part_count += 1

    # CHAPTERS ---------------------------------------------------------------------------------------------------------
    if file_book.rules["oneshot"]:
        # ONESHOT ONLY HAS ONE CHAPTER
        chapter_contents = main_soup.find("div", id="chapters").find("div", class_="userstuff")  # Get Text
        soup = build_oneshot(chapter_contents, "ao3")

        final_clean(soup)

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

            final_clean(soup)

            soup_to_file(soup, "final/" + str(part_count) + "-chapter.xhtml")
            part_count += 1

    # AFTERWORD --------------------------------------------------------------------------------------------------------
    afterword_search = main_soup.find("div", id="afterword").find("div", id="endnotes")  # Look for a valid afterword
    if afterword_search:  # If there is an afterword
        soup = build_afterword(afterword_search, "ao3")
        final_clean(soup)

        soup_to_file(soup, "final/" + str(part_count) + "-afterword.xhtml")



# FILE PART MANAGEMENT FUNCTIONS #######################################################################################
########################################################################################################################

# Pulls a preface from a soup
def build_preface(file_soup, format_type):
    """
    Builds a preface into a separate file from an ao3 soup.

    :param BeautifulSoup file_soup: The full ao3 soup. Needs to have access to full file.
    :param str format_type: NOT IMPLEMENTED
    :return: BeautifulSoup
    """
    # BUILD SKELETON FILE ----------------------------------------------------------------------------------------------
    epub_roles = {"epub:type": "preface", "role": "doc-preface"}
    soup = create_base_xhtml(epub_roles, "Preface")  # Basic File

    soup.section.append(soup.new_tag("h1", attrs={"class": "title"}))  # Heading
    soup.section.append(soup.new_tag("p", attrs={"class": "byline"}))  # Author byline
    soup.section.append(soup.new_tag("p", attrs={"class": "link"}))  # Archive of Our Own link

    soup.section.append(soup.new_tag("div", attrs={"class": "work-tags"}))  # Div for work tags
    soup.div.append(soup.new_tag("dl"))  # Start description list

    soup.section.append(soup.new_tag("div", attrs={"class": "summary"}))  # Div for work summary

    # ENTER BASIC DETAILS ----------------------------------------------------------------------------------------------
    # HEADING
    soup.h1.string = file_soup.find("h1").string

    # AUTHOR
    soup.find("p", class_="byline").string = "by "  # Start string
    soup.find("p", class_="byline").append(
        set_link(file_soup.find("div", class_="byline").a))  # Append author name to byline after checking links

    # WORK LINK
    work_link = file_soup.find("p", class_="message").find_all("a")
    soup.find("p", class_="link").string = "Posted originally on the "  # Start the link line
    soup.find("p", class_="link").append(set_link(work_link[0]))  # Add first link - Archive of Our Own
    soup.find("p", class_="link").append(" at ")  # bridge links
    soup.find("p", class_="link").append(set_link(work_link[1]))  # Add specific work link
    soup.find("p", class_="link").append(".")  # end line

    # TAG LIST ---------------------------------------------------------------------------------------------------------
    for tag in file_soup.dl:  # Get all description elements
        if tag.name == "dt":  # If description element title
            soup.dl.append(tag)
        if tag.name == "dd":  # If description element description
            for a in tag.find_all("a"):
                a.replace_with(set_link(a))  # Check all links in dd
            soup.dl.append(tag)

    # SUMMARY AND NOTES ----------------------------------------------------------------------------------
    # SUMMARY, ALL WORKS HAVE ONE
    summary_text = (file_soup.find("div", id="preface")
                    .find("p", string="Summary").find_next_sibling())  # Get the summary blocktext
    create_summary("Summary", summary_text, soup.find("div", class_="summary"))

    # NOTES, NEED TO CHECK FIRST
    notes_text = file_soup.find("div", id="preface").find("p",
                                                          string="Notes").find_next_sibling()  # Get the notes blocktext

    if notes_text:  # Check there is a note
        soup.section.append(soup.new_tag("div", attrs={"class": "notes"}))  # create div for work notes
        create_summary("Notes", notes_text, soup.find("div", class_="notes"))  # Make the note text

    return soup


def build_oneshot(file_soup, format_type):
    """
    Builds an ao3 oneshot.

    A 'oneshot' is a fic with only a single chapter. As such it does not need chapter notes (either beginning or end).

    :param Tag file_soup: The specific <div class="chapter"> part of the soup
    :param str format_type: NOT IMPLEMENTED
    :return: BeautifulSoup
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


def build_chapter(file_soup, format_type):
    """
    Builds an individual chapter and returns new Soup that with just the chapter.

    Checks that the chapter has a matching 'meta group' which has the chapter heading and the chapter notes (if any).
    If there is no matching group then return None.

    If valid endnotes can be found - include them

    :param Tag file_soup: The specific <div class="chapter"> part of the soup
    :param str format_type: NOT IMPLEMENTED
    :return: BeautifulSoup | None
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
    remove_dissallowed_attributes(soup)
    return soup


def build_afterword(file_soup, format_type):
    """
    Builds the afterword into a separate file from an ao3 soup.

    :param Tag file_soup: The soup of just the afterword text
    :param str format_type: NOT IMPLEMENTED
    :return: BeautifulSoup
    """
    # CREATE BASIC FILES
    epub_roles = {"epub:type": "afterword", "role": "doc-afterword"}
    soup = create_base_xhtml(epub_roles, "Afterword")
    # ADD CONTENT
    soup.section.append(soup.new_tag("div", attrs={"class": "notes"}))  # Create a div for notes
    create_summary("End Notes:", file_soup.blockquote, soup.div)

    return soup


# HELPER FUNCTIONS #####################################################################################################
########################################################################################################################

def create_base_xhtml(epub_roles, title):
    """
    Creates a basic xhtml file skeleton for content to be added into.

    :param dict epub_roles: A dictionary that contains information about the documents accessibility properties.
        Dictionary requires both a 'epub:type' and a 'role' (aria-role).
    :param str title: The string to be placed in the <title> tag

    :return: BeautifulSoup
    """
    # CREATE NEW XHTML FILE --------------------------------------------------------------------------------------------
    soup = BeautifulSoup("<!DOCTYPE html>", "html.parser")

    # CREATE NAMESPACES ------------------------------------------------------------------------------------------------
    soup.append(soup.new_tag("html"))  # Create html tag
    soup.html["xmlns"] = namespace_dict["xmlns"]
    soup.html["xmlns:epub"] = namespace_dict["xmlns:epub"]

    # CREATE HEAD ------------------------------------------------------------------------------------------------------
    soup.html.append(soup.new_tag("head"))  # Create head tag
    soup.html.head.append(soup.new_tag("meta"))  # Create meta tag
    soup.html.head.meta["charset"] = "utf-8"

    soup.html.head.append(soup.new_tag("title"))  # Create title tag, leave empty
    soup.find("title").string = title

    soup.html.head.append(
        soup.new_tag("link", attrs={"rel": "stylesheet", "type": "text/css", "href": "../styles.css"}))

    # CREATE BODY ------------------------------------------------------------------------------------------------------
    soup.html.append(soup.new_tag("body"))  # Create body tag
    soup.body.append(soup.new_tag("section"))  # Create section tag, needed for accessibility roles
    # ADD ACCESSIBILITY ROLES
    soup.body.section["epub:type"] = epub_roles["epub:type"]
    soup.body.section["role"] = epub_roles["role"]

    return soup  # Return prepared soup


def soup_to_file(soup, file_name):
    """
    Saves a soup to a .xhtml file

    :param BeautifulSoup soup: The soup to be saved to file
    :param str file_name: The file name to save the soup under. The .xhtml is added in function.

    :return: Void
    """
    output = open(file_name, "w")

    # ENCODE TO HTML INCASE THERE IS AN ISSUE
    soup.encode(formatter="html")
    output.write(str(soup))

    output.close()

    print("COMPLETED: " + file_name + "                      ", end='\r')  # Add whitespace to clear line


def set_link(tag):
    """
    A helper function to manage the no_links option.

    When given a <a> tag, check the NO_LINKS rule and remove link if true

    :param BeautifulSoup tag: The <a> ref that is being inserted
    :return: BeautifulSoup
    """
    if format_book.rules["no-links"]:
        soup = BeautifulSoup("", "html.parser")

        string_data = tag.string  # Get the string value of the old tag

        new_tag = soup.new_tag("i")  # Create replacement string
        new_tag.string = string_data

        return new_tag  # Return tag with link removed
    else:
        return tag  # Removed unchanged tag


def create_summary(title, summary_text, summary_div):
    """
    Creates a standard summary format for ao3 style notes and summary's

    Edits soup in place

    :param str title: The title of the summary
    :param Tag summary_text: The original summary text from file
    :param Tag summary_div: The new location for the summary
    :return: Void
    """
    soup = BeautifulSoup("", "html.parser")  # Create a soup

    summary_div.append(soup.new_tag("h2"))  # Add a title
    summary_div.h2.string = title
    summary_div.append(summary_text)  # Add the text
    summary_div.blockquote.unwrap()  # Remove blockquote


def final_clean(soup):
    """
    Do a final clean of the soup to remove any quirks

    :param BeautifulSoup soup: The soup being clean
    """
    clear_span(soup)
    clear_font(soup)

    clear_lone_nbsp(soup)

    remove_dissallowed_attributes(soup)


def remove_dissallowed_attributes(soup):
    """
    Removes any tags or attributes that are not valid for an epub.

    Edits soup in place

    :param BeautifulSoup soup: The soup to check for tags/attributes
    :return: Void
    """
    # ALIGN ATTRIBUTE
    attr_search = soup.find_all(align=True)
    for tag in attr_search:
        del tag["align"]  # Remove align tag
    # CENTER TAG
    for data in soup.find_all("center"):
        data.unwrap()
        if not type(data) is NavigableString:
            # Check if there is a tag to manage
            if "class" not in data:  # check to prevent overwriting of existing classes
                data["class"] = "center"
            else:
                temp = data["class"]
                data["class"] = temp + " center"


def clear_span(soup):
    """
    A function to remove all span tags from a given soup

    :param BeautifulSoup soup: The soup to scan for <span>
    """
    for data in soup.find_all("span"):
        if "class" not in data:  # If there is a class in the span ignore
            data.unwrap()


def clear_font(soup):
    """
    A function to remove all font tags from a given soup

    :param BeautifulSoup soup: The soup to scan for <font>
    """
    for data in soup.find_all("font"):
        data.unwrap()


def clear_lone_nbsp(soup):
    """
    Clear any nbsp that has been left on their own.

    :param BeautifulSoup soup: The soup to scan through
    """
    for data in soup.find_all(string="&nbsp;"):
        data.decompose()
