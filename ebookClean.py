### A tool to clean up html files generated by LibreOffice Writer into xhtml files for the creation of an epub using Beautiful Soup.

#IMPORTS ######################################################################################################
# Beautiful Soup imports. The main parser for the html files.
from bs4 import BeautifulSoup
from bs4 import Comment

# Custom classes
from htmlManager import cleanHTML
from book import book

import os.path
import re

# FILES NAMES AND PATHS ######################################################################################

# CHAPTER CONFIGIRATION --------------------------------------------------------------------------------------
chapter_count = 1 #The number of the starting chapter

#The folder of the uncleaned html files
chapter_folder = ".."
#The form of the chapter names - ".html" is implied
chapter_name = "Chapter {}"
#The destination of the finished files. 
final_folder = "final" 
#The name format for the final cleaned files ".xhtml" is implied
final_name = "chapter-{}" 

#Dictionary of any additional chapter files that do not fit the standard chapter conventions in chapter_name
#format: {file name: final file name}
#folders are the same as defined of chapter_path and final_path
additional_files = {"Epilogue":"epilogue"}

# OTHER PATHS ------------------------------------------------------------------------------------------------

#The name of the format file to be loaded - .txt is implied
format_name = "example"

# PROGRAM SET UP #############################################################################################

# COMMAND LINE ARGUMENTS -------------------------------------------------------------------------------------
#TODO: Add command line arguments

# BUILD PATHS ------------------------------------------------------------------------------------------------
chapter_path = "{}/{}.html".format(chapter_folder, chapter_name)  #The path of a chapter file
#print(chapter_path)
final_path = "{}/{}.xhtml".format(final_folder, final_name)       #The path of the final file
#print(final_path)
format_path = "format/{}.json".format(format_name)                 #The path of the format file
#print(format_path)

# FORMAT SETUP -----------------------------------------------------------------------------------------------
#Check if the book format file exists
if os.path.exists(format_path):
  #Open file
  format_file = open(format_path, 'r')
  #Create book information file
  thisBook = book(0, format_file)
  #thisBook = book.readFormat()

  #Close file
  format_file.close()
else:
  #No format provided - exit
  print("Error: Format does not exist")
  exit()

print(thisBook) 

# CREATING THE CLEANED FILES #################################################################################

# MAIN LOOP --------------------------------------------------------------------------------------------------
#Loop for main chapter files. Continue until an existing file cannot be found.
while os.path.exists(chapter_path.format(chapter_count)):

  #Open the chapter file
  file = open(chapter_path.format(chapter_count))
  

  #Create the soup for parsing
  soup = BeautifulSoup(file, 'html.parser')

  #Clean HTML
  cleanHTML(soup, thisBook, chapter_count)

  #Create output files
  output = open(final_path.format(chapter_count), "w")
  soup.encode(formatter="html") #encode to html
  output.write(str(soup)) #Write to file

  #Close files
  file.close()
  output.close()

  print("COMPLETED: " + final_path.format(chapter_count))

  chapter_count += 1 #increment chapter count

#Loop through all additional files provided
for file_name in additional_files:
  #Create path for additional files
  additional_path = "{}/{}.html".format(chapter_folder, file_name)
  additional_final = "{}/{}.xhtml".format(final_folder, additional_files[file_name])
  #Check if the file exists otherwise skip
  if os.path.exists(additional_path):

    #Open the chapter file
    file = open(additional_path)
    #Create the soup for parsing
    soup = BeautifulSoup(file, 'html.parser')

    #Clean HTML
    cleanHTML(soup, thisBook, "ADDITIONAL")

    #Create output files
    output = open(additional_final, "w")
    soup.encode(formatter="html") #encode to html

    output.write(str(soup)) #Write to file

    #Close files
    file.close()
    output.close()

    print("COMPLETED: " + additional_final)