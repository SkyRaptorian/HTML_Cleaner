from bs4 import BeautifulSoup
from bs4 import Comment

import re #Needed for string searches

def cleanHTML(soup, book, count):

    # INITIAL HTML SET UP ###################################################################################
    # NAMESPACES --------------------------------------------------------------------------------------------
    #ADD XHTML NAMESPACE
    soup.html["xmlns"] = "http://www.w3.org/1999/xhtml"
    #ADD EPUB TYPE NAME SPACE
    #TODO: epub:type stuff

    # MANAGE HTML HEAD --------------------------------------------------------------------------------------
    #MANAGE HEAD TAGS
    soup.title.string = book.bookName + " | " + book.chapterName.format(count) #Populate <title> tags

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
    for tag_type in book.styling: 
        #configure tags to be searchable, change style class, clear all attributes.
        for styled_tag in soup.find_all(tag_type):
            styled_tag["class"] = book.styling[tag_type]

    #replace em tags - LibreOffice Html Writer tags italics with <em>. If this behaviour is desired comment out.
    #for data in soup.find_all("em"):
    #    datastring = data.string
#
#        i_tag = soup.new_tag("i")
#        i_tag.string = datastring
#
#        data.replace_with(i_tag)

    # ADD SECTION BREAKS
    # MUST BE HR FOR ACCESSABILITY - ANY IMAGES MUST BE DONE IN CSS AS BACKGROUND IMAGE
    for l in soup.find_all("p", string=book.linebreakSymbol):
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
