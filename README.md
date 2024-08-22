HTML Cleaner is a python script that produces epub ready xhtml from pre-generated html.

Designed to work with LibreOffice Writer html output options to manage multiple html files at once.

It can also work with ao3 html downloads to split the work into parts to give the user more control over the output then
would be given if downloading the provided epub.

# FEATURES

- ***CSS Class Replace (INCOMPLETE)***

  Create rules for which elements have specific classes for consistency across multiple files.

- ***EPUB Ready xhtml***

  Produces xhtml ready to be put directly into an epub. Includes basic epub:type and aria-roles, needed namespaces,
  and removes any illegal tags or attributes.

- ***Strip Links***

  Provides an option to remove any links from provided html, replacing `<a>` tags with `<i>` tags


# GETTING STARTED

HTML Cleaner is a python script managed from the command line. It takes a JSON file from the format directory and
processes the html according to the provided rules.

## PREREQUISITES

HTML Cleaner runs on python3 and requires the following python libraries to run:

- Beautiful Soup

A requirements.txt has been provided.

    pip install -r requirements.txt

Alternatively each library can be installed indivifually

- Beautiful Soup

        pip install beautifulsoup4


## HTML SOURCES

HTML Cleaner requires html files to be provided in order to work. This section will go over where to get the html and
how to prepare the files for processing.

The currently supported sources are:

- Archive of Our Own (AO3) (https://archiveofourown.org)
- LibreOffice Writer

### Archive of Our Own

HTML Cleaner expects HTML provided from the archives download option which includes the full fic in one file. Not from
right-clicking the webpage and saving.

Select the download option on the top bar and select download -> HTML

As the HTML contains the entire work in one file no further changes need to be made.

For more information see the Archives policy here (https://archiveofourown.org/faq/downloading-fanworks)

**NOTE:** Currently there is no support for images and video within the HTML Cleaner program. Results may vary and be
unpredictable.

**NOTE:** There is currently no support for work skins.

### LibreOffice Writer

Generating the html files from LibreOffice Writer allows for pre-formatting to be done without having to get into html
tags or adjusting text from other sources by non-technical people.

**NOTE:** Currently there is no support for images and video within the HTML Cleaner program. Results may vary and be
unpredictable.

***Generating***

The HTML files can be generated in one of two ways.

1. _File -> Save As_

    Option one for generating HTML files through Writer is to open each file individually and File -> Save As... and
    selecting html from the filter bar.  
    This allows for each file to be given a new name if the files are saved under a different convention.  
    However for large amounts of files this can be time-consuming, and option two should be used instead.
2. _Command Line_
    
    LibreOffice has a command line interface (CLI) that can be used to quickly convert supported file types to html.

       libreoffice --convert-to html *.odt
    This command will create html files for all .odt files within the folder. 
    For more information see the `-h` command.

**_Naming_**

HTML files from LibreOffice Writer are expected to have each chapter or part contain in its own file, with all files 
found within a single folder.

The files should be of a consistent format (e.g. `Chapter 1.html`, `2-part.html`) with ascending numbers starting from one. The program
uses these numbers go through the full folder as such there can be no gaps in the numbering.

There is an additional option for a list of non-standard files that don't meet the selected naming convention (e.g.
`Epilogue.html`) however this requires more information to be given to the program which can become an annoyance.

For more information about naming conventions see the JSON file documentation.

## THE JSON FILE

The JSON files found within the `/format` directory are the means through which the program finds and interprets the html
files.

The JSON files are _required_. HTML Cleaner will not run without being provided one.

Two example files have been provided `example-lo.json` and `example-ao3.json` which will manage a LibreOffice html and
an AO3 html respectively.

### The General File

Every JSON file regardless of type requires these parameters:

    "version": 0,
    "file_type": "LibreOffice",
    "title": "Example",

The `version` number is just a check to make sure that the file is compatible with the current version of the software.  

The `file_type` is the important part as it defines what sort of file the program is expecting. It only has three valid 
values, `LibreOffice`, `ao3`, and `Series`.

The `title` is the main title of the work or book. It will be used to set the `<title>` tag, and for a series it will be
the name of the series rather than of an individual work.
---
### file_type: LibreOffice

The LibreOffice file_type defines a JSON that describes html files generated from LibreOffice. The provided `example-lo.json`
is of this type.

#### File Path Definitions

The JSON file directs the program to where to find the html files to parse. LibreOffice parsing takes an entire folder
at a time.

    "origin_folder": "..",
    "chapter_files": "Chapter {}",

The `origin_folder` value defines the folder to search for files. The path is relative to the 

`chapter_files` is a value that defines the pattern of the html files to be found. The `{}` are replaced with the chapter
number. For example: `Chapter 1.html, Chapter 2.html` and `1-part.html, 2-part.html` would have the patterns `Chapter {}` 
and `{}-part` with the file extension removed. There can only be one replacement value `{}` and it has to be consecutive 
numbers starting at 1.

    "chapter_format": "Chapter {}"

The `chapter_format` parameter is the name that chapters found with the `chapter_files` value will be saved under after
parsing. It follows the same pattern rules as the `chapter_files` value. Excludes the file extension (.xhtml)

    "additional_files": {
        "Prologue": {"title": "Prologue", "final_name": "prologue"},
        "Epilogue": {"title": "Epilogue", "final_name": "epilogue"}
    },

If there are files that don't match the pattern in `chapter_files` but still need to be included in the parse they can 
be included through the `additional_files` dictionary. If there are none leave empty.

The key is the name of the html file. `title` is the title of the file which gets appended into the `<title>` tag with
the main title from the top of the file. The `final_name` value is the name the file will get saved under excluding the 
file extension (.xhtml)

#### Formatting Rules

HTML Clean can make formatting adjustments to the work based on rules provided.

    "sectionbreak_symbol": "###",

`sectionbreak_symbol` defines a pattern to be replaced with a `<hr>` which can then be styled through css. Due to
accessibility reasons `<hr>`should be used for context breaks within the work, if an image is desired then it can be added
as a background image within the css file.  

The symbol will only be replaced if it is by itself on a line. 

#### Styling

HTML Clean can add css classes to certain areas of the document consistently across all documents.

    "style_rules": {
        "h1": "chapHeading",
        "body": "chapter"
    }

The `style_rules` dictionary has the document tag as a key and the css class as the value.

---
### file_type: ao3

The ao3 file_type defines a JSON that describes html files generated from the Archive of Our Own. The provided
`example-ao3.json` is of this type.

#### File Path Definitions

The JSON file directs the program to where to find the html files to parse.

    "main_file": "test/test",
    "oneshot": true,

`main_file` is a parameter that contains the html file to be parsed. The path to file is relative to the HTML Cleaner folder.

If the work is a oneshot, that is a work with only one chapter, set the `oneshot` flag to true. Otherwise leave false.

    "chapter_format": "Chapter {}"

The `chapter_format` parameter is the name that each chapter will be saved under. For more information about how the pattern
works see `chapter_files` in the _file_type: LibreOffice_ section.

#### Formatting Rules

HTML Clean can make formatting adjustments to the work based on rules provided.
    
    "no-links": true,

The `no-links` rule tells HTML Clean to remove any links from the work and replacing them with italics.

---
### file_type: Series

The ao3 file_type defines a JSON that describes html that make up a series. This is not currently implemented.


# USAGE



# ROADMAP

- [ ] Create series parser
- [ ] Improve Class styling 
- [ ] Add support for images
- [ ] Create cover files
- [ ] Compile into epub