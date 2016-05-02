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
                     
                     EVENT.KODI_PLAYBACK_STARTED_TEMPLATE % CONST.HOSTNAME: turnOffAll,
                     EVENT.KODI_PLAYBACK_PAUSED_TEMPLATE % CONST.HOSTNAME:  turnOnBottom,
                     EVENT.KODI_PLAYBACK_RESUMED_TEMPLATE % CONST.HOSTNAME: turnOffAll,
                     EVENT.KODI_PLAYBACK_STOPPED_TEMPLATE % CONST.HOSTNAME: turnOnAll,
                     EVENT.KODI_PLAYBACK_ENDED_TEMPLATE % CONST.HOSTNAME:   turnOnAll,
                     
                     EVENT.KODI_SCREENSAVER_ACTIVATED_TEMPLATE % CONST.HOSTNAME:   turnOffAll,
                     EVENT.KODI_SCREENSAVER_DEACTIVATED_TEMPLATE % CONST.HOSTNAME: turnOnTop,

                     EVENT.PERSONAL_TIME_TO_SLEEP: turnOffAll,
                   }

    #########################
    ###
    #
    def receiveData(self, data_dict):        
        
        ##########
        ## try autoresponse first
        #         
        self.autoResponder(data_dict)        
        
        if "method" in data_dict.keys():
            
            ##########
            ## cmds
            #                  
            if data_dict["method"] == METHOD.CMD and data_dict["params"]["target"] == self.plugin_name:
                for cmdstring in data_dict["params"]["cmds"]:
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
            if data_dict["method"] == METHOD.EVENT:
                for event in data_dict["params"]["events"]:

                    try:
                        if event in self.eventhandler.keys():
                            self.tasker.putTask(self.eventhandler[event])
                    except Exception as err:
                        logger.logError("Failed to handle event '%s' error: %s" % (event, str(err)))