#!/usr/bin/python
# # COLGATE - DWheeler - WheelerDA @ GitHub
# # 2014-07-18 - Initial release 0.5 Alpha minus

###########################################################################
##                                                                       ##
## Moodle .mbz Extract Utility
##                                                                       ##
## python 2.7 HACK
##                                                                       ##
###########################################################################
##                                                                       ##
## NOTICE OF COPYRIGHT                                                   ##
##                                                                       ##
## This program is free software; you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation; either version 3 of the License, or     ##
## (at your option) any later version.                                   ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
## GNU General Public License for more details:                          ##
##                                                                       ##
##          http:##www.gnu.org/copyleft/gpl.html                         ##
##                                                                       ##
###########################################################################

import xml.etree.ElementTree as etree
import fnmatch
import shutil
import os
import re
import datetime
import time
import sys

# Functions ###########################################################################
# locate # # # #
def locate(pattern, root=os.curdir):
    '''Locate all files matching supplied filename pattern in and below
    supplied root directory.'''
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)

# createOutputDirectories # # # #
def createOutputDirectories(destinationRoot):
    # create output subdirectories
    if os.path.exists(destinationRoot):
        print "\n$$$$ Directory " + sourceDir + " (" + destinationRoot + ") already exists! Overwriting existing files\n"
    else:
        os.mkdir(destinationRoot)

    for subdir in ("user","assignment","resource","forum","legacy"):
        if not os.path.exists(destinationRoot + subdir):
            os.mkdir(destinationRoot + subdir)

# 
# Initialize and add header to extract log file
def initializeLogfile(logfileName):
    logFileSpec = destinationRoot+logfileName

    global logfile
    logfile = open(logFileSpec,"w")
    if logfile.mode == 'w':
        logfile.write("Moodle Extract\n")
        logfile.write("Course: "+ shortname + " (" + fullname + ")\n")
        logfile.write(" Format: " + format + "\n")
        logfile.write(" Sections: " + topics + "\n")
        logfile.write("Extract started: " + timeStamp + "\n")
        logfile.write("------------------------\n")
        print ("Extract Log File: {0}".format(logFileSpec))
    else:
        print ("Error: unable to open {0} for writing".format(logFileSpec))

# /Functions ###########################################################################

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

print "\n##################\nextract-mbz.py\nextract moodle content from mbz backup (python v2.7)\n"
pipe = "|"
nl = "\n"
nArgs = len(sys.argv)
conflicted = 0

#print 'Number of arguments:', nArgs, 'arguments.'
#print 'Argument List:', str(sys.argv)

if nArgs < 2:
    print "usage: extract <input directory> \nYou must include the name of the subfolder containing the unzipped mbz contents...\n" 
    sys.exit()

if sys.argv[1] == '?':
    print "help:"
    print "\tusage: extract <input directory> \n\t\tYou must include the name of the subfolder containing the unzipped mbz contents..." 
    print "\n\t (Create a subfolder in this folder and unzip the .mbz into this subfolder... details somewhere else...)"
    print "\n\tcurrent objects extracted: Files, URLs"
    print "\tcurrent file types extracted: pdf|png|zip|rtf|sav|mp3|mht|por|xlsx?|docx?|pptx?\n"
    sys.exit()

sourceDir = str(sys.argv[1])

source = './'+sourceDir+'/'

if not os.path.exists(source + 'course/course.xml'):
    print "\nERROR: " + source + " does not appear to contain unzipped mbz contents (couldn't locate course.xml)\n"
    sys.exit()

destinationRoot      = './'+sourceDir+'-Extracted/'
createOutputDirectories(destinationRoot)

pattern     = re.compile('^\s*(.+\.(?:pdf|png|zip|rtf|sav|mp3|mht|por|xlsx?|docx?|pptx?))\s*$', flags=re.IGNORECASE)

# Get Course Info

courseTree = etree.parse(source + 'course/course.xml')
shortname = courseTree.getroot().find('shortname').text
fullname = courseTree.getroot().find('fullname').text
crn = courseTree.getroot().find('idnumber').text
format = courseTree.getroot().find('format').text
topics = courseTree.getroot().find('numsections').text
#print shortname + pipe + "fullname"

ts = time.time()
timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d-%H%M')
timeStampSeconds = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d-%H%M-%S')

print "Extracting backup of "+shortname+ " @ " + timeStamp + " to " + destinationRoot +"\n"

initializeLogfile("extract.log.txt")

# # #########################
# Process Course Files

fileTree = etree.parse(source + 'files.xml')
root = fileTree.getroot()

#print "Root: ", root

itemCount = 0
print "\nProcessing Course Files...";  # status
logfile.write("\n============\nCourse Files\n=============\n")

for rsrc in root:
	#print "Child id: ", rsrc.attrib
    fhash = rsrc.find('contenthash').text
    fname = rsrc.find('filename').text
    fcontext = rsrc.find('component').text

	#print "\tHash: '", fhash, "'"
	#print "\tName: '", fname, "'"
        #print "\tComponent: '", fcontext, "'"
    fname = fname.encode("utf-8","ignore")
    logfile.write ( "{0}|{1}|{2}|".format(fname, fhash, fcontext))
    hit = pattern.search(fname)

    if hit:
        itemCount += 1
		#print "\tMatch: ", hit.group(1)
        files = locate(fhash, source)
		#print "\tFiles: ", files
        logfile.write("|FILES\n")
        
        if fcontext == "user":
            destination = destinationRoot + "user/"
        elif fcontext == "mod_resource":
            destination = destinationRoot + "resource/"
        elif fcontext == "legacy":
            destination = destinationRoot + "legacy/"
        elif (fcontext == "mod_assignment") or (fcontext == "assignsubmission_file"):
            destination = destinationRoot + "assignment/"
        elif fcontext == "mod_forum":
            destination = destinationRoot + "forum/"
        else:
            destination = destinationRoot
                      
        for x in files:
            # print "Copying: ", x
            if os.path.exists(destination + fname):
                print " $$$$ File conflict!!!!! " + destination + fname 
                conflicted += 1
                shutil.copyfile(x, destination + fname + "-" + str(conflicted))
            else:
                shutil.copyfile(x, destination + fname)
        else: 
            logfile.write("NO FILES|\n")
    
# print "No Match: '", fname, "'"

print ("Extracted files = {0}".format(itemCount))
logfile.write ("\nExtracted files = {0}\n".format(itemCount))

print "\nProcessing Course Links (URLs)...";  # status

# # #########################
# Process Course Links (URLs)
webFilename = "courselinks.html"
webFileSpec = destinationRoot+webFilename

urlfile = open(webFileSpec,"w")
if urlfile.mode == 'w':
    urlfile.write("<html><title>Moodle Backup Extract</title><body><blockquote>")
    urlfile.write("<h3>Moodle Backup Extract..."+timeStamp+"</h1>")
    urlfile.write("<h2>"+shortname+" ("+fullname+")</h2>")
    urlfile.write("<h1>Course Links</h3>")
    urlfile.write("<ul>")
    logfile.write("\n============\nCourse Links\n=============\n")
    print ("Course Links: {0}".format(webFileSpec))
else:
    print ("Error: unable to open {0} for writing".format(webFileSpec))

print "===\nProcessing course urls..."

urlfiles = locate('url*',source + 'activities/')
itemCount = 0

for uf in urlfiles:
    itemCount += 1
    utree = etree.parse(uf)
    root = utree.getroot()
    for url in root:
        title = url.find('name').text
        titleText = title.encode("utf-8","ignore")
        address = url.find('externalurl').text
        addressText = address.encode("utf-8","ignore")
        intro = url.find('intro').text
        if intro:
            introText = intro.encode("utf-8","ignore")
 #           introText = introText.encode("ascii","ignore")
        else:
            introText = "..."

        logOutput = titleText + pipe + addressText + pipe + introText + pipe + nl 
        # print("{0}|{1}|{2}|".format(titleText,addressText,introText))
        
        HTMLOutput = '<li> <a href="'+addressText+'">'+titleText+'</a>'+introText+'</li>' + nl

        urlfile.write(HTMLOutput)
        logfile.write(logOutput)

if itemCount == 0:
    urlfile.write("<p>No links found!</p>")
    print("No course links found!")

logfile.write ("Extracted links = {0}".format(itemCount))

urlfile.close()
logfile.close()

# sym link
symLink = shortname.lower()+"-"+timeStampSeconds

if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
    print "Creative symlink for *nix systems..."
    if os.path.exists(symLink):
        print "symlink " + symLink + " already exists! CHECK!\n"
    else:
        print "Creating symlink " + symLink + " -> " + destinationRoot
        os.symlink(destinationRoot, symLink)

# clean up (remove) subdirectories not used
for subdir in ("forum", "legacy", "assignment", "user", "resource"):
    if not os.listdir(destinationRoot + subdir):
        os.rmdir(destinationRoot + subdir)
