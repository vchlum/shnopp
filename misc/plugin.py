#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import threading

from misc.communicator import Connector
from misc import logger

from config import CONST
from config import METHOD



class Plugin(Connector):
    """
    plugin template
    """

    def __init__(self, plugin_name = "plugin_general"):
        """
        :param plugin_name: name of plugin, used in core 
        """

        self.plugin_name = plugin_name             
        self.items = {}
        self.setSender()
        self.setReceiver()

        self.init()

        run_thread = threading.Thread(target=self.run)
        run_thread.setDaemon(True)
        run_thread.start()
        
    def getName(self):
        """
        name gather
        """
        
        return self.plugin_name
    
    def init(self):
        """
        plugin init function - can be overwritten
        """
        
        logger.logInfo("Define Init() in your plugin %s." % self.plugin_name)

    def run(self):
        """
        plugin run function - can be overwritten
        """
        
        logger.logDebug("Plugin %s run no service" % self.plugin_name)

    def setReceiver(self, handler = None):
        """
        receive handler setter
        :param handler: receiver
        """
        
        if not handler:
            handler = self.receiveData
        self.receiverhandler = handler

    def receiveData(self, data):
        """
        default receiver function
        """
        
        logger.logDebug("Input data '%s' not handled" % str(data).strip())
        return CONST.RET_OK

    def setSender(self, handler = None):
        """
        send handler setter 
        :param handler: sender
        """
        
        if not handler:
            handler = self.send
        self.sendhandler = handler
        
    def sendData(self, data):
        """
        standard send data function 
        :param data: data to send 
        """
        
        return self.sendhandler(data)        

    def askForItems(self):
        """
        ask other plugins for their items (supposed to be broadcasted)
        """
        
        self.sendJRPCRequest(METHOD.ITEMS, {"type":"request"})
        
    def autoResponder(self, data_dict):
        """
        check if incoming data consists of easily responsible requests
        :param data_dict: data to check
        """
        
        if not "method" in data_dict.keys():
            return
        
        if data_dict["method"] == METHOD.ITEMS and data_dict["params"]["type"] == "request":
            self.sendItems()

    def sendItems(self):
        """
        send plugin items to other plugins (supposed to be broadcasted)
        """
        
        result = {"type":METHOD.ITEMS, "plugin":self.getName(), "items":self.items}
        return self.sendJRPCResponse(result)