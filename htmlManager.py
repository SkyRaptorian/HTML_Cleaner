from bs4 import BeautifulSoup
from bs4 import Comment

def cleanHTML(soup, book, count):
    #clear head of non-title tags
    #print("Entered HTML Cleaner")
    soup.title.string = book.bookName + " | " + book.chapterName.format(count) #Populate <title> tags

    soup.find("meta", attrs={"name" : "generator"}).decompose() #Remove LibreOffice Writer meta tags
    soup.find("meta", attrs={"name" : "created"}).decompose()
    soup.find("meta", attrs={"name" : "changed"}).decompose()

    soup.find("style").decompose()

    #add dictionary styles
    for tag_type in book.styling: 
        #configure tags to be searchable, change style class, clear all attributes.
        for styled_tag in soup.find_all(tag_type):
            styled_tag["class"] = book.styling[tag_type]

    #replace em tags - LibreOffice Html Writer tags italics with <em>. If this behaviour is desired comment out.
    for data in soup.find_all("em"):
        datastring = data.string

        i_tag = soup.new_tag("i")
        i_tag.string = datastring

        data.replace_with(i_tag)

    #add linebreak
    for l in soup.find_all("p", string=book.linebreakSymbol):
        print("Linebreak in HTML")
        linebreak_tag = soup.new_tag("hr")
        linebreak_tag["class"] = "linebreak"

        l.replace_with(linebreak_tag)

    #clean unwanted tags and symbols - nbsp and font tags
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
