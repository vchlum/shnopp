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
    import pifacedigitalio
except ImportError:
    raise Exception('Importing pifacedigitalio failed!')



####################################################################
####################################################################
####################################################################
### LEDs behind my TV                                            ###
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
        self.pifacedigital = pifacedigitalio.PiFaceDigital()

        self.daytime = day_time.DayTime()

        self.tasker = tasks.Tasks()
        self.tasker.setTaskHandler(self.taskHandler)
     
    #########################
    ###
    #   
    def taskHandler(self, task):
        task(self)

    ######################################
    # piface functions (commands)        # 
    ######################################

    #########################
    ###
    #
    def toggle(self, arr):
        logger.logDebug("Toggle %s" % str(arr))
        for i in arr:
            if i in cfg.OUTPUT_CLOCKWISE:
                self.pifacedigital.output_pins[i].toggle()

    #########################
    ###
    #
    def turnOn(self, arr):
        logger.logDebug("Turn on %s" % str(arr))
        for i in arr:
            if i in cfg.OUTPUT_CLOCKWISE:
                self.pifacedigital.output_pins[i].turn_on()

    #########################
    ###
    #
    def turnOff(self, arr):
        logger.logDebug("Turn off %s" % str(arr))
        for i in arr:
            if i in cfg.OUTPUT_CLOCKWISE:
                self.pifacedigital.output_pins[i].turn_off()

    ######################################
    # event specific functions           # 
    ######################################
          
    #########################
    ###
    #    
    def blinkLEDs(self, leds):
        tmpvalues = {}
        for led in leds:
            tmpvalues[led] = self.pifacedigital.output_pins[led].value
            
        for i in range(3):
            self.toggle(leds)
            time.sleep(0.1)
            
        for led in leds:
            self.pifacedigital.output_pins[led].value = tmpvalues[led]
    
    #########################
    ###
    #        
    def blinkBottomLeft(self):
        self.blinkLEDs([cfg.OUTPUT_4])
     
    #########################
    ###
    #   
    def blinkBottomRight(self):
        self.blinkLEDs([cfg.OUTPUT_5])
     
    #########################
    ###
    #   
    def blinkTopLeft(self):
        self.blinkLEDs([cfg.OUTPUT_6])
     
    #########################
    ###
    #   
    def blinkTopRight(self):
        self.blinkLEDs([cfg.OUTPUT_7])

    #########################
    ###
    #
    def turnOnAll(self):
        if self.daytime.isShining():
            logger.logDebug("Doing nothing due to day time.")
            return
        self.turnOn(cfg.OUTPUT_ALL)    

    #########################
    ###
    #                          
    def turnOffAll(self):
        self.turnOff(cfg.OUTPUT_ALL)

    #########################
    ###
    #
    def turnOnBottom(self):
        if self.daytime.isShining():
            logger.logDebug("Doing nothing due to day time.")
            return
        self.turnOn(cfg.OUTPUT_BOTTOM)  
    
    #########################
    ###
    #                   
    def turnOnTop(self):
        if self.daytime.isShining():
            logger.logDebug("Doing nothing due to day time.")
            return
        self.turnOn(cfg.OUTPUT_TOP)

    ######################################
    # receiver and received cmd handlers # 
    ######################################

    cmdhandler = { CMD.ON: turnOn,
                   CMD.OFF: turnOff,
                   CMD.TOGGLE: toggle,
                 }
            
    eventhandler = { EVENT.CECLOG_ACTIVESOURCE_OSMC:          blinkBottomLeft,
                     EVENT.CECLOG_ACTIVESOURCE_CHROMECAST:    blinkTopLeft,
                     EVENT.CECLOG_ACTIVESOURCE_PLAYSTATION_4: blinkBottomRight,
                     
                     EVENT.KODI_PLAYBACK_STARTED: turnOffAll,
                     EVENT.KODI_PLAYBACK_PAUSED:  turnOnBottom,
                     EVENT.KODI_PLAYBACK_RESUMED: turnOffAll,
                     EVENT.KODI_PLAYBACK_STOPPED: turnOnAll,
                     EVENT.KODI_PLAYBACK_ENDED:   turnOnAll,
                     
                     EVENT.KODI_SCREENSAVER_ACTIVATED:   turnOffAll,
                     EVENT.KODI_SCREENSAVER_DEACTIVATED: turnOnTop,

                     EVENT.PERSONAL_TIME_TO_SLEEP: turnOffAll,
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
                        cmd = None
                        path = self.items
                        for p in cmdstring.split(CONST.DELIMITER):
                            cmd = p
                            path = path[p]
                            
                        adresses = path
                        
                        try:
                            iter_test = iter(adresses)
                        except TypeError, te:
                            adresses = (adresses,)
    
                        self.cmdhandler[cmd](self, adresses)
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
                        self.tasker.putTask(self.eventhandler[event])
                except Exception as err:
                    logger.logError("Failed to handle event '%s' error: %s" % (event, str(err)))

        ##########
        ## requests
        #
        if REQ.TAG in data.keys():
            for request in data[REQ.TAG]:
                if request  == REQ.ITEMS:
                    self.sendMyItems()
