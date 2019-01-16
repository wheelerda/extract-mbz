extract-mbz
===========

Extract content from Moodle backup files (.mbz)

Background: 
Working on a request from a professor I was surprised to find that there wasn't yet a tool to extract a Moodle backup archive, much as bFree does for Blackboard archives. After finding only this proof of concept python script on the web (http://www.reades.com/2012/11/29/mb-archives/) I figured I'd take a stab at it. My initial release efforts (I've used it for a few extract requests already) are here. Documentation is below and my python script is attached. 

And lest I seem too dismissive, I owe my efforts to Jon Reades and his proof of concept python script. Thanks!

Status:
Updated with code from Andrew Ruether to enhance extract - more items are extracted and are now displayed (nicely) via an html file. 

Right now this is still a command line script which may need some more work, but it does grab most of the files in a Moodle course and all the URLs. The files are simply dumped into appropriate folders with their original names (or simple conflict resolution of their name). The URLs are collected into an HTML file. A log file is generated with more information. 

There are many more useful items for retrieval (student roster, grades, ...) and more improvements to be made. See details below. 

We've tested it so far on:

    Mac OS 10.10/11 with native Python
  
extracting Files and URLs.

## Requirements:
Python 2.7 (and for the uninitiated, note that newer is not better - Python 3 does not run a v2.7 program!) 

    Installed with most Mac OS X versions

    Available for download for Windows from Python.Org
    
You will also need two python libraries: slugify and python-magic (find mac installation instructions here https://github.com/ahupp/python-magic)

## Usage:

    Create a directory (folder) for your archive and place your .mbz file in it.
    If you choose to relocate the python program files from your downloads folder to a new location, 
    make sure the tachyons.css file is still in the same directory as your copy of the extract-mbz.py file.
    Unzipping your Moodle .mbz file prior to running the script is not necessary.  You can run the 
    script straight on the .mbz file with no changes.
    
    Command line - <path-to-python-program-if-needed>python extract-mbz.py <full-path-to-your-mbz-file>
    
    If successful, you will see a new folder created in the directory where your archive is, with the same title 
    as the original .mbz file.

    Within this new folder, look for the subfolder titled <shortname-of-your-course>. This subfolder contains all 
    the documents from the course, along with a html document containing the all the links and text from that course.
    If you're sharing the course contents with someone else and don't want to include the extraneous xml files, you can 
    send just this <shortname-of-your-course> subfolder without missing any files or breaking the links in the html document.
        
    For Command line help - use a question mark as the parameter - <path-to-python-program-if-needed>python extract-mbz.py ?  

## Technical Background:
As already stated, I've been hacking at this so far, and not using detailed specifications to develop this tool. The proof of concept showed me how to get files and I figured out how to get URLs by looking at the .xml files. This probably won't work for more complex data structures such as grades so we'll need to understand the details of the Moodle Backup process. 

As expected, Moodle uses an xml format to create course backups. The xml files and related documents are compressed in a .zip format archive. One uses any unzip-compatible program to retrieve the contents. 

http://docs.moodle.org/dev/Backup_2.0_for_developers

Information page: https://sites.google.com/a/colgate.edu/dwheeler/Home/extract-mbz
