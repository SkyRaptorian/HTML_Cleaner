import book

def readFormat(file) -> book:
    hasStyle = False
    hasLBSymbol = False

    for line in file:
        boundary = line.find(":")
        word = line[:boundary]

        match word:
            case "TITLE":
                title = line[boundary+1:]
            case "CHAP":
                chapter = line[boundary+1:]
            case "LINEBREAK":
                hasLBSymbol = True
                print("Found Linebreak")
                linebreak = line[boundary+1:len(line)-1]
                print(linebreak)
            case "STYLE":
                hasStyle = True
                style = {}

                workingDict = line[boundary+1:] #collect everypart of the string without STYLE:
                #startDict = workingDict.find("(") #find the start of the brackets
                #endDict = workingDict.find(")") #find the end of the brackets
                nextTerm = workingDict.find(":") #tags are seperated by : find the next one until it runs out.
                nextSpace = workingDict.find(".")

                while nextTerm != -1: #loop until no more tags
                    tag = workingDict[:nextTerm]
                    rule = workingDict[nextTerm+1:nextSpace]

                    workingDict = workingDict[nextSpace+1:]
                    nextTerm = workingDict.find(":")
                    nextSpace = workingDict.find(".")

                    style[tag] = rule
                    #print(style)
    
    #Create book based off read in data
    if hasStyle:
        if hasLBSymbol:
            abook = book.book(title, chapter, linebreak, style)
            return abook
        else:
            abook = book.book(title, chapter, style)
            return abook
    elif hasLBSymbol:
        abook = book.book(title, chapter, linebreak)
        return abook
    else:
        abook = book.book(title, chapter)
        return abook
