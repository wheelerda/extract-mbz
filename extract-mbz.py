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
from slugify import slugify

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

# Unique filename
# From http://code.activestate.com/recipes/577200-make-unique-file-name/
# By Denis Barmenkov <denis.barmenkov@gmail.com>
def add_unique_postfix(fn):
    if not os.path.exists(fn):
        return fn

    path, name = os.path.split(fn)
    name, ext = os.path.splitext(name)

    make_fn = lambda i: os.path.join(path, '%s(%d)%s' % (name, i, ext))

    for i in xrange(2, sys.maxint):
        uni_fn = make_fn(i)
        if not os.path.exists(uni_fn):
            return uni_fn

    return None


# Given a filename with extension, slugify the base part of the filename
def make_slugified_filename(filename):
	path, name = os.path.split(filename)
	name, ext = os.path.splitext(filename)
	return os.path.join(path, "%s%s" % (slugify(name), ext))



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

source = sourceDir #'./'+sourceDir+'/'

if not os.path.exists(os.path.join(source, 'course', 'course.xml')):
    print "\nERROR: " + source + " does not appear to contain unzipped mbz contents (couldn't locate course.xml)\n"
    sys.exit()

if not os.path.exists(os.path.join(source,  'moodle_backup.xml')):
    print "\nERROR: " + source + " does not appear to contain unzipped mbz contents (couldn't locate moodle_backup.xml)\n"
    sys.exit()

destinationRoot      = os.path.join(sourceDir, '-Extracted/')
createOutputDirectories(destinationRoot)

# Copy HTML support files to extracted folder
script_dir = os.path.dirname(os.path.realpath(__file__))
shutil.copy(os.path.join(script_dir, "tachyons.css"),os.path.join(sourceDir, '-Extracted/'))



pattern     = re.compile('^\s*(.+\.(?:pdf|png|zip|rtf|sav|mp3|mht|por|xlsx?|docx?|pptx?))\s*$', flags=re.IGNORECASE)

# Get Course Info
courseTree = etree.parse(os.path.join(source, 'course', 'course.xml'))
shortname = courseTree.getroot().find('shortname').text
fullname = courseTree.getroot().find('fullname').text
crn = courseTree.getroot().find('idnumber').text
format = courseTree.getroot().find('format').text
topics = courseTree.getroot().find('numsections').text
#print shortname + pipe + "fullname"


# Get Moodle backup file info
backupTree = etree.parse(os.path.join(source, 'moodle_backup.xml'))
backupTreeRoot = backupTree.getroot()
activities = backupTreeRoot.find("information").find("contents").find("activities")

ts = time.time()
timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d-%H%M')
timeStampSeconds = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d-%H%M-%S')

print "Extracting backup of "+shortname+ " @ " + timeStamp + " to " + destinationRoot +"\n"

initializeLogfile("extract.log.txt")


html_header = '''
<head>
	<title>Moodle Backup Extract</title>
	<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
	<link rel="stylesheet" type="text/css" href="tachyons.css">
</head>'''






##########################
# Process each section
webFilename = "coursesections.html"
webFileSpec = os.path.join(destinationRoot, webFilename)


urlfile = open(webFileSpec,"w")
if urlfile.mode == 'w':
    urlfile.write("<html>%s<body><blockquote>" % html_header)
    urlfile.write("<h3>Moodle Backup Extract..."+timeStamp+"</h3>")
    urlfile.write("<h2>"+shortname+" ("+fullname+")</h2>")
    urlfile.write("<h1>Course Sections</h1>")
    logfile.write("\n============\nCourse Sections\n=============\n")
    print ("Course Sections: {0}".format(webFileSpec))
else:
    print ("Error: unable to open {0} for writing".format(webFileSpec))

print "===\nProcessing course sections..."

itemCount = 0

for s in backupTreeRoot.findall("./information/contents/sections")[0].findall("section"):
	
	section_title = s.find("title").text
	print "\nNow processing section id: %s (%s)" % (s.find("sectionid").text, section_title)

	# If the section title is just a number that is the same value as the item count, prepend a string
	if section_title == str(itemCount):
		if itemCount == 0:
			section_title = "Section Header"
		else:
			section_title = "Section %s" % section_title


		


	HTMLOutput = "<h2>%s</h2>" % section_title 


	# Open section file
	section_file_root = etree.parse(os.path.join(source, s.find("directory").text, "section.xml"))
	section_summary = section_file_root.find("summary").text	
	if section_summary:
		HTMLOutput += "<p>%s</p>" % section_summary.encode("utf-8", errors='ignore')
	HTMLOutput += "<ul>"
	
	
	section_sequence = section_file_root.find("sequence").text.split(',')
	
	# Folder path for section (if needed)
	section_file_dir = os.path.join(destinationRoot, "section_%03d" % itemCount)



	for item in section_sequence:
		# Look for this item in the Moodle backup file
		item_xpath = ".//*[moduleid='%s']" % item
		item_title = activities.find(item_xpath).find("title").text  # default
		modulename = activities.find(item_xpath).find("modulename").text
		
		print "Found %s (item #: %s) titled %s" % (modulename, item, item_title)
		
		if modulename == "resource":
			# Get link to file
			resourceTree = etree.parse(os.path.join(source, 'activities', 'resource_%s' % item,  'inforef.xml'))
			file_listing = resourceTree.findall("fileref/file")		
			files = etree.parse(os.path.join(source,'files.xml')) # Look in files area to get name of file
		
			for f in file_listing:
				file_id = f.find("id").text
	
				filename = files.find("file[@id='%s']/filename" % file_id).text
				
				if filename != "." and filename != "":
	
					# Copy the file to a folder for this section
					if not os.path.exists(section_file_dir):
						os.makedirs(section_file_dir)
					filename = make_slugified_filename(filename)
					contenthash = files.find("file[@id='%s']/contenthash" % file_id).text
			
					destination = add_unique_postfix(os.path.join(section_file_dir, filename))
					file = os.path.join(source, "files", contenthash[:2], contenthash)
			
					#print "  File resource id %s (%s).  Copy from %s to %s" % (file_id, filename, file, destination)
			
					shutil.copyfile(file, destination)
					
					file_url = "./section_%03d/%s" % (itemCount, filename)
					item_title = "<a href='%s'>%s</a>" % (file_url, item_title)
			
    			
	
		elif modulename == "url":
			# Get url link
			urlTree = etree.parse(os.path.join(source, 'activities', 'url_%s' % item,  'url.xml'))
			url = urlTree.find("url/externalurl").text
			print "Url id %s" % file_id
		
			item_title = "<a href='%s' target='_blank'>%s</a>" % (url, item_title)
		
		elif modulename == "page":
			page_title = activities.find(item_xpath).find("title").text  # default
			page_xml_file = activities.find(item_xpath).find("directory").text
			
			# Open page file
			page_tree = etree.parse(os.path.join(source, page_xml_file,  'page.xml'))
			page_content = page_tree.find("page/content").text
		
			# Save page as a standalone HTML file
			if not os.path.exists(section_file_dir):
				os.makedirs(section_file_dir)
			pageFilename = make_slugified_filename("%s.html" % page_title)
			pageFilePath = os.path.join(section_file_dir, pageFilename)
			pageFilePath = add_unique_postfix(pageFilePath)
			
			pagefile = open(pageFilePath,"w")
			if pagefile.mode == 'w':
				pagefile.write("<html>%s<body><blockquote>" % html_header)
				pagefile.write("<h2>%s (%s)</h2>" % (fullname, shortname))
				pagefile.write("<h1>%s</h1>" % page_title)			
				pagefile.write(page_content.encode("utf-8", errors='ignore'))
				pagefile.close()
			
			page_url = "./section_%03d/%s" % (itemCount, pageFilename)
			item_title = "<a href='%s'>%s</a>" % (page_url, page_title)
		
		elif modulename == "folder":
			# Get folder info
			folder_title = activities.find(item_xpath).find("title").text  
			folder_xml_file = activities.find(item_xpath).find("directory").text
			
			# Open folder info to get description
			folder_tree = etree.parse(os.path.join(source, folder_xml_file,  'folder.xml'))
			folder_desc = folder_tree.find("folder/intro").text
			
			# Open inforef file to get file list
			resourceTree = etree.parse(os.path.join(source, folder_xml_file,  'inforef.xml'))
			file_listing = resourceTree.findall("fileref/file")		
			files = etree.parse(os.path.join(source,'files.xml')) # Look in files area to get name of file
		
			folder_html = "<div><ul>"
			for f in file_listing:
				file_id = f.find("id").text
	
				original_filename = files.find("file[@id='%s']/filename" % file_id).text
				
				if original_filename != "." and original_filename != "":
	
					# Copy the file to a folder for this section
					if not os.path.exists(section_file_dir):
						os.makedirs(section_file_dir)
					filename = make_slugified_filename(original_filename)
					contenthash = files.find("file[@id='%s']/contenthash" % file_id).text
			
					destination = add_unique_postfix(os.path.join(section_file_dir, filename))
					file = os.path.join(source, "files", contenthash[:2], contenthash)
			
					shutil.copyfile(file, destination)
					
					file_url = "./section_%03d/%s" % (itemCount, filename)
					folder_html += "<li><a href='%s'>%s</a></li>" % (file_url, original_filename)
			
			folder_html += "</ul></div>"
			item_title = "%s Folder%s" % (folder_title, folder_html)
				
		
		
		else:
			item_title += " (%s)" % modulename
		



		#item_path = activities.find(item_xpath).find("directory").text
		HTMLOutput += "<li>%s</li>" % item_title

	
	logOutput = section_title + nl 
	HTMLOutput += "</ul>"

	urlfile.write(HTMLOutput)
	logfile.write(logOutput)
	itemCount += 1

if itemCount == 0:
    urlfile.write("<p>No sections found!</p>")
    print("No sections found!")

logfile.write ("Extracted sections = {0}".format(itemCount))

urlfile.close()




# # #########################
# Process Course Files

fileTree = etree.parse(os.path.join(source,'files.xml'))
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
            destination = os.path.join(destinationRoot, "user")
        elif fcontext == "mod_resource":
            destination = os.path.join(destinationRoot, "resource")
        elif fcontext == "legacy":
            destination = os.path.join(destinationRoot, "legacy")
        elif (fcontext == "mod_assignment") or (fcontext == "assignsubmission_file"):
            destination = os.path.join(destinationRoot, "assignment")
        elif fcontext == "mod_forum":
            destination = os.path.join(destinationRoot, "forum")
        else:
            destination = destinationRoot
                      
        for x in files:
            # print "Copying: ", x
            if os.path.exists(os.path.join(destination,fname)):
                print " $$$$ File conflict!!!!! " + destination + fname 
                conflicted += 1
                shutil.copyfile(x, os.path.join(destination, fname + "-" + str(conflicted)))
            else:
                shutil.copyfile(x, os.path.join(destination, fname))
        else: 
            logfile.write("NO FILES|\n")
    
# print "No Match: '", fname, "'"

print ("Extracted files = {0}".format(itemCount))
logfile.write ("\nExtracted files = {0}\n".format(itemCount))



# # #########################
# Process Course Links (URLs)

print "\nProcessing Course Links (URLs)...";  # status
webFilename = "courselinks.html"
webFileSpec = os.path.join(destinationRoot, webFilename)

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

urlfiles = locate('url*', os.path.join(source, 'activities'))
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
    if not os.listdir(os.path.join(destinationRoot, subdir)):
        os.rmdir(os.path.join(destinationRoot, subdir))
