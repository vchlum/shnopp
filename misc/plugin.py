#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import threading
import json
import sys

from misc.communicator import Connector
from misc import logger

from config import CONST
from config import REQ
from config import CFG



####################################################################
####################################################################
####################################################################
### plugins                                                      ###
####################################################################
####################################################################
####################################################################



############################################
### plugin template class                ###
############################################
############################################
############################################

class Plugin(Connector):

    #########################
    ###
    #
    def __init__(self, plugin_name = "plugin_general"):

        self.plugin_name = plugin_name             
        self.items = {}
        self.setSender()
        self.setReceiver()

        self.init()

        run_thread = threading.Thread(target=self.run)
        run_thread.setDaemon(True)
        run_thread.start()
        
    #########################
    ###
    #
    def getName(self):
        return self.plugin_name
    
    #########################
    ###
    #
    def init(self):
        logger.logInfo("Define Init() in your plugin %s." % self.plugin_name)

    #########################
    ###
    #
    def run(self):
        logger.logDebug("Plugin %s run no service" % self.plugin_name)

    #########################
    ###
    #
    def setReceiver(self, handler = None):
        if not handler:
            handler = self.receiveData
        self.receiverhandler = handler

    #########################
    ###
    #
    def receiveData(self, data, mydata):
        logger.logDebug("Input data '%s' not handled" % str(data).strip())
        return CONST.RET_OK

    #########################
    ###
    #
    def setSender(self, handler = None):
        if not handler:
            handler = self.send
        self.sendhandler = handler
        
    #########################
    ###
    #
    def sendData(self, data):
        return self.sendhandler(data)        

    #########################
    ###
    #
    def sendMyItems(self, name = None):
        if not name:
            name = self.getName()

        return self.sendDictonary({REQ.ITEMS:{name:self.items}})
