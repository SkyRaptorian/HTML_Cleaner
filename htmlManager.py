from bs4 import BeautifulSoup
from bs4 import Comment

import re #Needed for string searches

#Namespace dictionary xmlns:epub=
namespace_dict = {
    "xmlns": "http://www.w3.org/1999/xhtml",
    "xmlns:epub": "http://www.idpf.org/2007/ops"
}

def clean_html_libreOffice(soup, book, count):

    # INITIAL HTML SET UP ###################################################################################
    # NAMESPACES --------------------------------------------------------------------------------------------
    #ADD XHTML NAMESPACE
    soup.html["xmlns"] = "http://www.w3.org/1999/xhtml"
    #ADD EPUB TYPE NAME SPACE
    #TODO: epub:type stuff

    # MANAGE HTML HEAD --------------------------------------------------------------------------------------
    #MANAGE HEAD TAGS
    soup.title.string = book.book_title + " | " + book.chapter_format.format(count) #Populate <title> tags

    #REMOVE LibreOffice META TAGS
    soup.find("meta", attrs={"name" : "generator"}).decompose()
    soup.find("meta", attrs={"name" : "created"}).decompose()
    soup.find("meta", attrs={"name" : "changed"}).decompose()

    #REMOVE DEFAULT STYLING
    soup.find("style").decompose()

    #MANAGE HTML BODY ---------------------------------------------------------------------------------------
    #REMOVE AUTO GENERATED BODY TAG ATTRIBUTES
    attr_to_del = soup.body.attrs.copy() #Copy dictionary to prevent iteration issues
    for attr in attr_to_del:
        del soup.body[attr] # Delete all attributes in the body tag
    
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
    # CREATE FILES ##########################################################################################
    # CREATE FOREWORD/PREFACE -------------------------------------------------------------------------------
    soup = create_base_xhtml()
    soup.body.append(soup.new_tag("section")) #Add section

    #ADD ACCESSABILITY ROLES
    soup.body.section["epub:type"] = "preface"
    soup.body.section["role"] = "doc-preface"

    #The tag that all the work will be done in. The "Working directory"
    working_tag = soup.body.section

    #Create Preface Skeleton
    #Add Heading
    working_tag.append(soup.new_tag("h1", attrs={"class":"ficTitle"}))
    #Add bylines
    working_tag.append(soup.new_tag("p", attrs={"class":"byline"}))
    working_tag.append(soup.new_tag("p", attrs={"class":"message"}))


    #Search First Preface Paragraph
    search_contents = main_soup.find("div", id="preface").find("p").contents
    #Add fic title
    working_tag.h1.string = search_contents[1].string

    #Posted Orginally byline
    working_tag.find("p", class_="message").string = search_contents[3]
    working_tag.find("p", class_="message").string.insert_after(search_contents[4])

    #Add author byline
    working_tag.find("p", class_="byline").string = "by "
    working_tag.find("p", class_="byline").string.insert_after(main_soup.find("div", class_="byline").a)

    #Create details/tags description list
    working_tag.append(soup.new_tag("div", attrs={"class":"meta"}))
    working_tag.div.append(soup.new_tag("dl"))

    #get dl from original file
    search_contents = main_soup.find("dl")
    for element in search_contents.children:
        if (element.name == "dt"):
            working_tag.div.dl.append(element)
        if (element.name == "dd"):
            working_tag.div.dl.append(element)
    
    #Find preface summary and notes
    search_contents = main_soup.find("div", id="preface").find_all("blockquote")

    #ADD SUMMARY
    working_tag.append(soup.new_tag("div", attrs={"class":"summary"}))
    #Create heading
    working_tag.find("div", class_="summary").append("h2")
    working_tag.find("div", class_="summary").string = "Summary"
    #Create block quote
    working_tag.find("div", class_="summary").append(soup.new_tag("blockquote"))
    for element in search_contents[0]:
        working_tag.find("div", class_="summary").blockquote.append(element)
    
    #print(main_soup.find("div", id="preface").find("p", string="Notes"))
    #Check if there are notes
    if main_soup.find("div", id="preface").find_all("p", string="Notes"):
        #ADD WORK NOTES
        working_tag.append(soup.new_tag("div", attrs={"class":"notes"}))
        working_tag.find("div", class_="notes").append("h2")
        working_tag.find("div", class_="notes").string = "Notes"
        #Create block quote
        working_tag.find("div", class_="notes").append(soup.new_tag("blockquote"))
        for element in search_contents[1]:
            working_tag.find("div", class_="notes").blockquote.append(element)

    soup_to_file(soup, "test.html")

    #START CHAPTERS -----------------------------------------------------------------------------------------
    working_search = main_soup.find("div", id="chapters") #The chapter area of the main file
    #Get all chapter text
    chapter_contents = working_search.find_all("div", class_="userstuff")
    chapter_count = 1 #counter for the chapter - used to find endnotes

    #loop through all chpater contets
    for chapter_text in chapter_contents:
        soup = create_base_xhtml()
        soup.body.append(soup.new_tag("section")) #Add section

        #ADD ACCESSABILITY ROLES
        soup.body.section["epub:type"] = "chapter"
        soup.body.section["role"] = "doc-chapter"

        #ADD CSS
        soup.body.section["class"] = "ficText"

        #The tag that all the work will be done in. The "Working directory"
        working_tag = soup.body.section

        #Get meta group
        meta_group = chapter_text.find_previous_sibling("div", class_="meta group")
        endnote = chapter_text.find_next_sibling("div", id=("endnotes"+str(chapter_count))) #only return endnote for this chapter

        #Create headings
        if (meta_group):
            #print(meta_group.h2.string)
            working_tag.append(soup.new_tag("h1"))
            working_tag.h1.string = meta_group.h2.string

            soup.find("title").string = meta_group.h2.string

            #if their are chapter notes
            if (meta_group.find("blockquote")):
                #print("Chapter Note")
                working_tag.append(soup.new_tag("div", attrs={"class": "summary"}))
                #Summary title
                working_tag.find("div", class_="summary").append(soup.new_tag("h2"))
                working_tag.find("div", class_="summary").h2.string = "Summary"

                #Summary in blockquote
                working_tag.find("div", class_="summary").append(soup.new_tag("blockquote"))
                for tag in meta_group.find("blockquote").find_all("p"):
                    #print(tag)
                    working_tag.find("blockquote").append(tag)
        else:
            #If no meta group there may be an inner split - ignore
            continue

        #Chapter text
        #working_tag.append(soup.new_tag("div", attrs={"class":"body_text"}))
        working_tag.append(chapter_text)
        #print(type(chapter_text.children))
        working_tag.find("div", class_="userstuff")["class"] = "body_text"
        #Add text

        #REMOVE DISALLOWED ATTRIBUTES TODO: Move to method that covers more attributes
        #align is html only not for epub
        attr_search = soup.find_all(align=True)
        for tag in attr_search:
            del tag["align"] #Remove align tag
        #print(attr_search)

        #Chapter end notes
        if (endnote):
            #print(endnote)
            working_tag.append(soup.new_tag("div", attrs={"class":"endnotes"}))
            working_tag.find("div", class_="endnotes").append(soup.new_tag("h2"))
            working_tag.find("div", class_="endnotes").h2.string = "End Notes"

            working_tag.find("div", class_="endnotes").append(soup.new_tag("blockquote"))

            for tag in endnote.find("blockquote").find_all("p"):
                    #print(tag)
                    working_tag.find("div", class_="endnotes").blockquote.append(tag)

        

       #final FORMATTING
       # 

        soup_to_file(soup, "final/test" + str(chapter_count) + ".xhtml")
        chapter_count += 1
    
    #AFTERWORD
    if (main_soup.find("div", id="afterword").find("div", id="endnotes")):
        working_search = main_soup.find("div", id="afterword").find("div", id="endnotes")

        soup = create_base_xhtml()
        soup.body.append(soup.new_tag("section")) #Add section

        #ADD ACCESSABILITY ROLES
        soup.body.section["epub:type"] = "afterword"
        soup.body.section["role"] = "doc-afterword"

        #ADD TITLE
        soup.find("title").string = "Afterword"

        #ADD CONTENT
        soup.find("section").append(soup.new_tag("h1"))
        soup.body.section.h1.string = "End Notes"

        soup.find("section").append(working_search.find("blockquote"))
        del soup.find("blockquote")["class"] #Delete class from blockquote

        soup_to_file(soup, "final/afterword.xhtml")
        

    

#############################################################################################################
###### HELPER FUNCTIONS #####################################################################################
#############################################################################################################

def create_base_xhtml() -> BeautifulSoup:
    #CREATE NEW XHTML FILE
    soup = BeautifulSoup("<!DOCTYPE html>", "html.parser")

    #CREATE SHELL -----------------------------------------------------
    soup.append(soup.new_tag("html")) #Create html tag
    soup.html["xmlns"] = namespace_dict["xmlns"]
    soup.html["xmlns:epub"] = namespace_dict["xmlns:epub"]

    # CREATE HEAD -----------------------------------------------------
    soup.html.append(soup.new_tag("head")) #Create head tag
    soup.html.head.append(soup.new_tag("meta")) #Create meta tag
    soup.html.head.meta["charset"] = "utf-8"

    soup.html.head.append(soup.new_tag("title")) #CReate title tag, leave empty

    soup.html.head.append(soup.new_tag("link", attrs={"rel":"stylesheet", "type":"text/css", "href":"../styles.css"}))

    # CREATE BODY -----------------------------------------------------
    soup.html.append(soup.new_tag("body")) #Create body tag

    return soup

def soup_to_file(soup, file_name):
    output = open(file_name, "w")
    soup.encode(formatter="html") #encode to html
    output.write(str(soup)) #Write to file