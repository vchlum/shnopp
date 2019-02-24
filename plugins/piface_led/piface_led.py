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
    import pifacedigitalio
except ImportError:
    raise Exception('Importing pifacedigitalio failed!')



class Plugin(plugin.Plugin):
    """
    pi face - LEDs behind my TV
    """
    
    def init(self):
        """
        initialize
        """
                
        self.items = CFG.ITEMS_PIFACE_LED
        self.pifacedigital = pifacedigitalio.PiFaceDigital()

        self.daytime = day_time.DayTime()

        self.tasker = tasks.Tasks()
        self.tasker.setTaskHandler(self.taskHandler)
     
    def taskHandler(self, task):
        """
        handle task, task is function
        :param task: function to run
        """
        
        task(self)

    def toggle(self, arr):
        """
        piface functions (toggle command)
        :param arr: all items will be handled
        """
        
        logger.logDebug("Toggle %s" % str(arr))
        for i in arr:
            if i in CFG.OUTPUT_CLOCKWISE:
                self.pifacedigital.output_pins[i].toggle()

    def toggleall(self):
        """
        piface functions (toggle all)
        """
        
        self.toggle(CFG.OUTPUT_ALL)
        
    def toggleBottom(self):
        """
        toggle on bottom two
        """
              
        self.toggle(CFG.OUTPUT_BOTTOM)  
    
    def toggleTop(self):
        """
        toggle on top two
        """ 
        
        self.toggle(CFG.OUTPUT_TOP)  

    def turnOn(self, arr):
        """
        piface functions (on command)
        :param arr: all items will be handled
        """
        
        logger.logDebug("Turn on %s" % str(arr))
        for i in arr:
            if i in CFG.OUTPUT_CLOCKWISE:
                self.pifacedigital.output_pins[i].turn_on()

    def turnOff(self, arr):
        """
        piface functions (off command)
        :param arr: all items will be handled
        """
        
        logger.logDebug("Turn off %s" % str(arr))
        for i in arr:
            if i in CFG.OUTPUT_CLOCKWISE:
                self.pifacedigital.output_pins[i].turn_off()

    def blinkLEDs(self, leds):
        """
        event specific functions
        double blink
        :param leds: arra of items to blink 
        """
        tmpvalues = {}
        for led in leds:
            tmpvalues[led] = self.pifacedigital.output_pins[led].value
            
        for i in range(3):
            self.toggle(leds)
            time.sleep(0.1)
            
        for led in leds:
            self.pifacedigital.output_pins[led].value = tmpvalues[led]
    
    def blinkBottomLeft(self):
        """
        blink specific led
        """
        
        self.blinkLEDs([CFG.OUTPUT_4])
     
    def blinkBottomRight(self):
        """
        blink specific led
        """
        
        self.blinkLEDs([CFG.OUTPUT_5])
     
    def blinkTopLeft(self):
        """
        blink specific leds
        """
        
        self.blinkLEDs([CFG.OUTPUT_6])
     
    def blinkTopRight(self):
        """
        blink specific leds
        """
        
        self.blinkLEDs([CFG.OUTPUT_7])

    def turnOnAll(self):
        """
        turn on all
        """
        
        if self.daytime.isShining():
            logger.logDebug("Doing nothing due to day time.")
            return
        self.turnOn(CFG.OUTPUT_ALL)    

    def turnOffAll(self):
        """
        turn off all
        """
        
        self.turnOff(CFG.OUTPUT_ALL)

    def turnOnBottom(self):
        """
        turn on bottom two
        """
              
        if self.daytime.isShining():
            logger.logDebug("Doing nothing due to day time.")
            return
        self.turnOn(CFG.OUTPUT_BOTTOM)  
    
    def turnOnTop(self):
        """
        turn on top two
        """
        
        if self.daytime.isShining():
            logger.logDebug("Doing nothing due to day time.")
            return
        self.turnOn(CFG.OUTPUT_TOP)

    # receiver and received cmd handlers
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

                     EVENT.CEC_KEYPRESSED_TEMPLATE % 113: turnOffAll,
                     EVENT.CEC_KEYPRESSED_TEMPLATE % 114: toggleall,
                     EVENT.CEC_KEYPRESSED_TEMPLATE % 115: toggleTop,
                     EVENT.CEC_KEYPRESSED_TEMPLATE % 116: toggleBottom,

                     EVENT.RF433_PRESSED % 1572015379: turnOnAll,
                     EVENT.RF433_PRESSED % 1572013339: turnOffAll,
                     EVENT.RF433_PRESSED % 4196961755: turnOnAll,
                     EVENT.RF433_PRESSED % 4196959703: turnOffAll,
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

            # events
            if data_dict["method"] == METHOD.EVENT:
                for event in data_dict["params"]["events"]:

                    try:
                        if event in self.eventhandler.keys():
                            self.tasker.putTask(self.eventhandler[event])
                    except Exception as err:
                        logger.logError("Failed to handle event '%s' error: %s" % (event, str(err)))
