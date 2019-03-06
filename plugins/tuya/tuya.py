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
from config import CFG

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
                
        self.items = CFG.ITEMS_TUYA

        self.daytime = day_time.DayTime()
        
        self.tasker = tasks.Tasks()
        
    def setStatus(self, devid, status, switch=1):
        key = CFG.DEVICES[devid]
        tuyadev = pytuya.OutletDevice(devid, key[0], key[1])
        tuyadev.set_status(status, switch)
        
    def rf433Pressed(self, keycode):
        if keycode in CFG.RF433 and CFG.RF433[keycode][0]:
            self.setStatus(CFG.RF433[keycode][0], CFG.RF433[keycode][1])

    eventhandler = {EVENT.RF433_PRESSED.split(CONST.DELIMITER)[0]: rf433Pressed,
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
                        #if not cmdstring.split(CONST.DELIMITER)[0] in cfg.MY_PLACES:
                        #    continue

                        dev_cmd = self.items
                        for p in cmdstring.split(CONST.DELIMITER):
                            dev_cmd = dev_cmd[p]

                        if (len(dev_cmd) == 2):
                            self.setStatus(dev_cmd[0], dev_cmd[1])

                        if (len(dev_cmd) == 3):
                            self.setStatus(dev_cmd[0], dev_cmd[1], dev_cmd[2])

                    except Exception as err:
                        logger.logError("Failed to run command %s: %s" % (str(cmdstring), str(err)))

            # events
            if data_dict["method"] == METHOD.EVENT:
                for event in data_dict["params"]["events"]:

                    try:
                        event = event.split(CONST.DELIMITER)
                        if len(event) == 2:
                            if event[0] in self.eventhandler.keys():
                                self.eventhandler[event[0]](self, event[1])
                        elif event in self.eventhandler.keys():
                            self.eventhandler[event](self)
                    except Exception as err:
                        logger.logError("Failed to handle event '%s' error: %s" % (event, str(err)))
