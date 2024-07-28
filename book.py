### Class to manage the details of the ebook for parameter passing
### AUTHOR: SkyRaptorian
### CREATION DATE: 11 AUG 2023
### MODIFIED DATE: 11 AUG 2023

class book:
    def __init__(self, name, chapter, linebreak = "###", styleRules = {}):
        self.bookName = name
        self.chapterName = chapter
        self.linebreakSymbol = linebreak
        self.styling = styleRules