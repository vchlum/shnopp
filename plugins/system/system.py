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
from config import METHOD
from config import CFG



class Plugin(plugin.Plugin):
    """
    system plugin - shutdown, restart system, ... 
    """
    
    def init(self):
        """
        initialize
        """
        
        self.items = CFG.ITEMS_SYSTEM
    
 
    def systemCmd(self, cmd):
        """
        run the command
        """
        logger.logInfo("Running command '%s'" % cmd)
        os.system(cmd) 

    eventhandler = { 
                     #EVENT.PERSONAL_TIME_TO_SLEEP: ,
                   }

    def receiveData(self, data_dict):        
        """
        handle received data
        :param data_dict: received data
        """
        
        myhostname = socket.gethostname()
        
        # try autoresponse first
        self.autoResponder(data_dict)

        if "method" in data_dict.keys():

            # cmds
            if data_dict["method"] == METHOD.CMD and data_dict["params"]["target"] == self.plugin_name:
                for cmdstring in data_dict["params"]["cmds"]:
                    try:
                        cmd = self.items
                        for p in cmdstring.split(CONST.DELIMITER):
                            cmd = cmd[p]
                            
                        self.systemCmd(cmd)
                    except Exception as err:
                        logger.logError("Failed to run command %s: %s" % (str(cmdstring), str(err)))
