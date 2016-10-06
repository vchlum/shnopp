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
    import pi_switch
except ImportError:
    raise Exception('Importing pi_switch failed!')



class Plugin(plugin.Plugin):
    """
    plugin for remote ac sockets 
    """
    
    def init(self):
        """
        initialize
        """
                
        self.items = cfg.ITEMS
        self.ac_socks = pi_switch.RCSwitchSender()
        self.ac_socks.enableTransmit(0)
        self.ac_socks.setProtocol(1)
        
        self.daytime = day_time.DayTime()
        
        self.tasker = tasks.Tasks()
        self.tasker.setTaskHandler(self.transmitCode)

    def transmitCode(self, code):
        """
        transmit code using pi_switch
        :param code: code to transmit
        """
        
        try:
            logger.logDebug("Transmitting code: %s" % str(code))
            self.ac_socks.send(code)
            time.sleep(cfg.MIN_TRNASMIT_INTERVAL)
        except Exception as err:
            logger.logError("Transmitting AC socket code error: %s" % str(err))

    def morningLight(self):
        """
        event specific function
        never used yet
        """
        
        if self.daytime.isShining():
            logger.logDebug("Doing nothing due to day time.")
            return
        
        code = self.items[cfg.AC_SOCK_1][cfg.AC_SOCK_1_1][CMD.ON]
        self.tasker.putTask(code)

        code = self.items[cfg.AC_SOCK_1][cfg.AC_SOCK_1_2][CMD.ON]
        self.tasker.putTask(code)

    def iWannaDarkness(self):
        """
        event specific function
        turn off all
        """
        
        for place in self.items.keys():
            if cfg.AC_SOCK_ALL in self.items[place]:
                code = self.items[place][cfg.AC_SOCK_ALL][CMD.OFF]
                self.tasker.putTask(code)

    def lightLighting(self):
        """
        event specific function
        """
        
        if self.daytime.isShining():
            logger.logDebug("Doing nothing due to day time.")
            return
        
        code = self.items[cfg.AC_SOCK_2][cfg.AC_SOCK_2_2][CMD.ON]
        self.tasker.putTask(code)

    def goForBeerLighting(self):
        """
        event specific function
        """
        
        if self.daytime.isShining():
            logger.logDebug("Doing nothing due to day time.")
            return
        
        ac_sockets_to_on = [(cfg.AC_SOCK_2, cfg.AC_SOCK_2_2, CMD.ON), 
                            (cfg.AC_SOCK_3, cfg.AC_SOCK_2_4, CMD.ON)]

        for (place, ac_sock, sockcmd) in ac_sockets_to_on:
            code = self.items[place][ac_sock][sockcmd]
            self.tasker.putTask(code)

    eventhandler = { EVENT.KODI_PLAYBACK_STARTED_TEMPLATE % CONST.HOSTNAME: iWannaDarkness,
                     EVENT.KODI_PLAYBACK_PAUSED_TEMPLATE % CONST.HOSTNAME:  goForBeerLighting,
                     EVENT.KODI_PLAYBACK_RESUMED_TEMPLATE % CONST.HOSTNAME: iWannaDarkness,
                     EVENT.KODI_PLAYBACK_STOPPED_TEMPLATE % CONST.HOSTNAME: lightLighting,
                     EVENT.KODI_PLAYBACK_ENDED_TEMPLATE % CONST.HOSTNAME:   goForBeerLighting,
                     
                     EVENT.KODI_SCREENSAVER_ACTIVATED_TEMPLATE % CONST.HOSTNAME:   iWannaDarkness,
                     EVENT.KODI_SCREENSAVER_DEACTIVATED_TEMPLATE % CONST.HOSTNAME: lightLighting,

                     EVENT.PERSONAL_TIME_TO_WAKEUP: morningLight,
                     EVENT.PERSONAL_TIME_TO_SLEEP: iWannaDarkness,
                     
                     EVENT.CEC_KEYPRESSED_TEMPLATE % 113: iWannaDarkness,
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