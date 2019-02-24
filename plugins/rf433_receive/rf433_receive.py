#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import time
import argparse
import signal

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
    from rpi_rf import RFDevice
except ImportError:
    raise Exception('Importing rpi_rf failed!')



class Plugin(plugin.Plugin):
    """
    plugin for rf433_receive
    """
    
    def init(self):
        """
        initialize
        """
                
        self.rfdevice = None

        signal.signal(signal.SIGINT, self.exithandler)
        self.rfdevice = RFDevice(27)

    def exithandler(signal, frame):
        """
        exit signal handler
        """
        self.rfdevice.cleanup()

    def run(self):
        """
        plugin main
        """
        
        self.rfdevice.enable_rx()
        timestamp = None

        while True:
            if self.rfdevice.rx_code_timestamp != timestamp:
                timestamp = self.rfdevice.rx_code_timestamp
                logger.logDebug("rf433_receive code: %s length %s protocol: %s" % (str(self.rfdevice.rx_code), str(self.rfdevice.rx_pulselength), str(self.rfdevice.rx_proto)))
                self.sendEvents(EVENT.RF433_PRESSED % self.rfdevice.rx_code)

            time.sleep(CFG.SLEEP_INTERVAL)

        rfdevice.cleanup()

    eventhandler = { }

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
                        if not cmdstring.split(CONST.DELIMITER)[0] in cfg.MY_PLACES:
                            continue

                        for p in cmdstring.split(CONST.DELIMITER):
                            path = path[p]
                            
                        code = path
                        self.tasker.putTask(code)
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
