#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import inspect
import sys
import os



####################################################################
####################################################################
####################################################################
### logging system                                               ###
####################################################################
####################################################################
####################################################################

loghandler = None  

############################################
### redirecting output to file           ###
############################################
############################################
############################################

#########################
###
#
class Ownstdout(object):
    write_handler = None

    def __init__(self, write_handler):
        self.write_handler = write_handler
        
    def write(self, data):
        if len(data.strip()) > 0:
            self.write_handler(data.strip())

#########################
###
#
class Ownstderr(Ownstdout):
    def write(self, data):
        if len(data.strip()) > 0:
            self.write_handler(data.rstrip())

#########################
###
#
def startLogFile(name, f, fn):
    import logging
    global loghandler
    logging.basicConfig(format=f, filename=fn, level=logging.DEBUG)
    l = logging.getLogger(name)
    loghandler = l.info

#########################
###
#
def redirectStdout():
    global loghandler
    sout = Ownstdout(loghandler)
    sys.stdout = sout

#########################
###
#
def redirectStderr():
    global loghandler
    serr = Ownstderr(loghandler)
    sys.stderr = serr

#########################
###
#
def closestdIO():
    sys.stdout.flush()
    sys.stderr.flush()
    si = file(os.devnull, 'r')
    so = file(os.devnull, 'a+')
    se = file(os.devnull, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
    
    
    
############################################
### print output                         ###
############################################
############################################
############################################

#########################
###
#
def logData(data):
    if isinstance(data, basestring):
	    print data
    else:
        print "[%s] %s: %s" % data

#########################
###
#
def logInfo(data):
    filetag = os.path.basename((inspect.getouterframes(inspect.currentframe())[1])[1])
    messagetag = "INFO"
    logData((messagetag, filetag, data))

#########################
###
#
def logDebug(data):
    filetag = os.path.basename((inspect.getouterframes(inspect.currentframe())[1])[1])
    messagetag = "DEBUG"
    logData((messagetag, filetag, data))

#########################
###
#
def logWarning(data):
    filetag = os.path.basename((inspect.getouterframes(inspect.currentframe())[1])[1])
    messagetag = "WARNING"
    logData((messagetag, filetag, data))

#########################
###
#	
def logError(data):
    filetag = os.path.basename((inspect.getouterframes(inspect.currentframe())[1])[1])
    messagetag = "ERROR"
    logData((messagetag, filetag, data))

#########################
###
#	
def logTest(data):
    filetag = os.path.basename((inspect.getouterframes(inspect.currentframe())[1])[1])
    messagetag = "TEST"
    logData((messagetag, filetag, data))

