#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import threading

from misc.communicator import Connector
from misc import logger

from config import CONST
from config import METHOD



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
    def receiveData(self, data):
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
    def askForItems(self):
        self.sendJRPCRequest(METHOD.ITEMS, {"type":"request"})
        
    #########################
    ###
    #
    def autoResponder(self, data_dict):
        if not "method" in data_dict.keys():
            return
        
        if data_dict["method"] == METHOD.ITEMS and data_dict["params"]["type"] == "request":
            self.sendItems()

    #########################
    ###
    #
    def sendItems(self):
        result = {"type":METHOD.ITEMS, "plugin":self.getName(), "items":self.items}
        return self.sendJRPCResponse(result)