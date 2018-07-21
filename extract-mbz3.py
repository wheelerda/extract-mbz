#!/usr/bin/python3

# COLGATE - DWheeler - WheelerDA @ GitHub 
# # 2014-07-18 - Initial release 0.5 Alpha minus

# convert by  Lasith - LasithNiro @ Github
# 2018-07-21 


###########################################################################
##                                                                       ##
## Moodle .mbz Extract Utility
##                                                                       ##
## python 3.5 HACK
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
import magic
import zipfile
import tarfile
from importlib import reload


# http://stackoverflow.com/questions/21129020/how-to-fix-unicodedecodeerror-ascii-codec-cant-decode-byte
if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding("utf-8")

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
        print ("\n$$$$ Directory " + sourceDir + " (" + destinationRoot + ") already exists! Overwriting existing files\n")
    else:
        os.mkdir(destinationRoot)

    for subdir in ("user","assignment","resource","forum","legacy", "course"):
        if not os.path.exists(os.path.join(destinationRoot, subdir)):
            os.mkdir(os.path.join(destinationRoot, subdir))


# Initialize and add header to extract log file
def initializeLogfile(logfileName):
    logFileSpec = os.path.join(destinationRoot,logfileName)

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
	return os.path.join(path, "%s%s" % (slugify(unicode(name)), ext))

# Unzip the mbz file and extract the contents
def unzip_mbz_file(mbz_filepath):

    # Make folder to contain contentes of unzipped mbz file
    base_dir = os.path.dirname(mbz_filepath)
    mbz_filename, extension = os.path.splitext(os.path.basename(mbz_filepath))
    unzip_folder = mbz_filename
    i = 1
    while unzip_folder in os.listdir(base_dir):
        unzip_folder = "%s_%d" % (mbz_filename, i)
        i+=1

    fullpath_to_unzip_dir = os.path.join(base_dir, unzip_folder)
    if not os.path.exists(fullpath_to_unzip_dir):
        os.mkdir(fullpath_to_unzip_dir)

	# Older version of mbz files are zip files
	# Newer versions are gzip tar files
	# Figure out what file type we have an unzip appropriately

    # https://stackoverflow.com/questions/25286176/how-to-use-python-magic-5-19-1
    m = magic.open(magic.MAGIC_NONE)
    m.load()
    fileinfo = m.file(mbz_filepath)

    if ('Zip archive data' in fileinfo):        
	    with zipfile.ZipFile(mbz_filepath, 'r') as myzip:myzip.extractall(fullpath_to_unzip_dir)

    elif 'gzip compressed data' in fileinfo:
        tar = tarfile.open(mbz_filepath)
        tar.extractall(path=fullpath_to_unzip_dir)
        tar.close()
		
    else:
        print ("Can't figure out what type of archive file this is")
        return -1
	
    return fullpath_to_unzip_dir

# /Functions ###########################################################################

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

print ("\n##################\nextract-mbz.py\nextract moodle content from mbz backup (python v2.7)\n")
pipe = "|"
nl = "\n"
nArgs = len(sys.argv)
conflicted = 0

#print 'Number of arguments:', nArgs, 'arguments.'
#print 'Argument List:', str(sys.argv)

if nArgs < 2:
    print ("usage: extract <path to Moodle backup mbz file> \n")
    sys.exit()

if sys.argv[1] == '?':
    print ("help:")
    print ("\tusage: extract <path to Moodle backup mbz file>")
    print ("\n\tcurrent objects extracted: Files, URLs")
    print ("\tcurrent file types extracted: pdf|png|gif|zip|rtf|sav|mp3|mht|por|xlsx?|docx?|pptx?\n")
    sys.exit()

mbz_filepath = str(sys.argv[1])

if not os.path.exists(mbz_filepath):
    print ("\nERROR: " + mbz_filepath + " does not appear to exist\n")
    sys.exit()

source = unzip_mbz_file(mbz_filepath)

if not os.path.exists(os.path.join(source, 'course', 'course.xml')):
    print ("\nERROR: " + source + " does not appear to contain unzipped mbz contents (couldn't locate course.xml)\n")
    sys.exit()

if not os.path.exists(os.path.join(source,  'moodle_backup.xml')):
    print ("\nERROR: " + source + " does not appear to contain unzipped mbz contents (couldn't locate moodle_backup.xml)\n")
    sys.exit()