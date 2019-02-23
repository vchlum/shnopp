#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import time

from misc import logger
from misc import plugin
from misc import day_time
from misc import tasks

from config import CONST
from config import CMD
from config import EVENT
from config import METHOD

import cfg

try:
    import pytuya
except ImportError:
    raise Exception('Importing pytuya failed!')



class Plugin(plugin.Plugin):
    """
    plugin for tuya
    """
    
    def init(self):
        """
        initialize
        """
                
        self.items = cfg.ITEMS

        self.daytime = day_time.DayTime()
        
        self.tasker = tasks.Tasks()

    eventhandler = { 
                   }

    def receiveData(self, data_dict):     
        """
        handle received data
        :param data_dict: received data
        """
           
        # try autoresponse first    
        self.autoResponder(data_dict)
                
        if "method" in data_dict.keys():
            
            # cmds
            if data_dict["method"] == METHOD.CMD and data_dict["params"]["target"] == self.plugin_name:
                for cmdstring in data_dict["params"]["cmds"]:
                    try:
                        path = self.items
                        #if not cmdstring.split(CONST.DELIMITER)[0] in cfg.MY_PLACES:
                        #    continue

                        dev_cmd = self.items
                        for p in cmdstring.split(CONST.DELIMITER):
                            dev_cmd = dev_cmd[p]

                        key = cfg.DEVICES[dev_cmd[0]]

                        tuyadev = pytuya.OutletDevice(dev_cmd[0], key[0], key[1])
                        tuyadev.set_status(dev_cmd[1])
                        
                    except Exception as err:
                        logger.logError("Failed to run command %s: %s" % (str(cmdstring), str(err)))

            # events
            if data_dict["method"] == METHOD.EVENT:
                for event in data_dict["params"]["events"]:

                    try:
                        if event in self.eventhandler.keys():
                            self.eventhandler[event](self)
                    except Exception as err:
                        logger.logError("Failed to handle event '%s' error: %s" % (event, str(err)))
