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
from config import REQ

import cfg

try:
    import pi_switch
except ImportError:
    raise Exception('Importing pi_switch failed!')



####################################################################
####################################################################
####################################################################
### AC sockets pluggin                                           ###
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
        self.ac_socks = pi_switch.RCSwitchSender()
        self.ac_socks.enableTransmit(0)
        self.ac_socks.setProtocol(1)
        
        self.daytime = day_time.DayTime()
        
        self.tasker = tasks.Tasks()
        self.tasker.setTaskHandler(self.transmitCode)

    #########################
    ###
    #
    def transmitCode(self, code):
        try:
            logger.logDebug("Transmitting code: %s" % str(code))
            self.ac_socks.send(code)
            time.sleep(cfg.MIN_TRNASMIT_INTERVAL)
        except Exception as err:
            logger.logError("Transmitting AC socket code error: %s" % str(err))

    ######################################
    # event specific functions           # 
    ######################################

    #########################
    ###
    #
    def morningLight(self):
        if self.daytime.isShining():
            logger.logDebug("Doing nothing due to day time.")
            return
        
        code = self.items[cfg.AC_SOCK_1][cfg.AC_SOCK_1_2][CMD.ON]
        self.tasker.putTask(code)

        code = self.items[cfg.AC_SOCK_1][cfg.AC_SOCK_1_3][CMD.ON]
        self.tasker.putTask(code)

    #########################
    ###
    #
    def iWannaDarkness(self):
        for place in self.items.keys():
            if cfg.AC_SOCK_ALL in self.items[place]:
                code = self.items[place][cfg.AC_SOCK_ALL][CMD.OFF]
                self.tasker.putTask(code)

    #########################
    ###
    #
    def lightLighting(self):
        if self.daytime.isShining():
            logger.logDebug("Doing nothing due to day time.")
            return
        
        code = self.items[cfg.AC_SOCK_2][cfg.AC_SOCK_2_2][CMD.ON]
        self.tasker.putTask(code)

    #########################
    ###
    #
    def goForBeerLighting(self):
        if self.daytime.isShining():
            logger.logDebug("Doing nothing due to day time.")
            return
        
        ac_sockets_to_on = [(cfg.AC_SOCK_2, cfg.AC_SOCK_2_2, CMD.ON), 
                            (cfg.AC_SOCK_2, cfg.AC_SOCK_2_3, CMD.ON)]

        for (place, ac_sock, sockcmd) in ac_sockets_to_on:
            code = self.items[place][ac_sock][sockcmd]
            self.tasker.putTask(code)

    ######################################
    # receiver and received cmd handlers # 
    ######################################

    eventhandler = { EVENT.KODI_PLAYBACK_STARTED: iWannaDarkness,
                     EVENT.KODI_PLAYBACK_PAUSED:  goForBeerLighting,
                     EVENT.KODI_PLAYBACK_RESUMED: iWannaDarkness,
                     EVENT.KODI_PLAYBACK_STOPPED: lightLighting,
                     EVENT.KODI_PLAYBACK_ENDED:   goForBeerLighting,
                     
                     EVENT.KODI_SCREENSAVER_ACTIVATED:   iWannaDarkness,
                     EVENT.KODI_SCREENSAVER_DEACTIVATED: lightLighting,

                     EVENT.PERSONAL_TIME_TO_WAKEUP: morningLight,
                     EVENT.PERSONAL_TIME_TO_SLEEP: iWannaDarkness,
                   }

    #########################
    ###
    #
    def receiveData(self, data, mydata):        
        logger.logDebug("Received data: '%s'" % str(data))
        
        ##########
        ## data for me
        # 
        if mydata:
            if CMD.TAG in mydata.keys():
                for cmdstring in mydata[CMD.TAG]:
                    try:
                        path = self.items
                        for p in cmdstring.split(CONST.DELIMITER):
                            path = path[p]
                            
                        code = path
                        self.tasker.putTask(code)
                    except Exception as err:
                        logger.logError("Failed to run command %s: %s" % (str(cmdstring), str(err)))

        ##########
        ## events
        #
        if EVENT.TAG in data.keys():
            for event in data[EVENT.TAG]:
                logger.logDebug("Received event: %s" % str(event))

                try:
                    if event in self.eventhandler.keys():
                        self.eventhandler[event](self)
                except Exception as err:
                    logger.logError("Failed to handle event '%s' error: %s" % (event, str(err)))

        ##########
        ## requests
        #
        if REQ.TAG in data.keys():
            for request in data[REQ.TAG]:
                if request  == REQ.ITEMS:
                    self.sendMyItems()
