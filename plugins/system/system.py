#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import time
import os
import socket

from misc import logger
from misc import plugin

from config import CONST        
from config import CMD
from config import EVENT
from config import REQ

import cfg

####################################################################
####################################################################
####################################################################
#system                                                          ###
####################################################################
####################################################################
####################################################################



############################################
### plugin main class                    ###
############################################
############################################
############################################

class Plugin(plugin.Plugin):
    
    #########################
    ###
    #
    def init(self):
        self.items = cfg.ITEMS
    
    #########################
    ###
    #    
    def systemCmd(self, cmd):
        os.system(cmd) 

    ######################################
    # receiver and received cmd handlers # 
    ######################################

    eventhandler = { 
                     #EVENT.PERSONAL_TIME_TO_SLEEP: ,
                   }

    #########################
    ###
    #
    def receiveData(self, data, mydata):        
        logger.logDebug("Received data: '%s'" % str(data))

        myhostname = socket.gethostname()  

        ##########
        ## data for me
        # 
        if mydata:
            if CMD.TAG in mydata.keys():
                for cmdstring in mydata[CMD.TAG]:
                    try:
                        cmd = self.items
                        for p in cmdstring.split(CONST.DELIMITER):
                            cmd = cmd[p]
                            
                        self.systemCmd(cmd)
                    except Exception as err:
                        logger.logError("Failed to run command %s: %s" % (str(cmdstring), str(err)))
                    
        ##########
        ## requests
        #
        if REQ.TAG in data.keys():
            for request in data[REQ.TAG]:
                if request  == REQ.ITEMS:
                    self.sendMyItems()
