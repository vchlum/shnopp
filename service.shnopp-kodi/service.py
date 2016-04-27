#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xbmc
import xbmcgui

import logging
import json

from misc import communicator
from config import CFG
from config import EVENT


APP_NAME = "shnopp-kodi"

LOG_FILE = CFG.DIR_VAR + APP_NAME.lower() + ".log"

class KodiMonitor(xbmc.Monitor):
    
    def __init__ (self):          
        xbmc.Monitor.__init__(self)
        self.logger = None

    def onCleanStarted(self, *arg):
        self.logger.debug("Cleaning library started")

    def onCleanFinished(self, *arg):
        self.logger.debug("Cleaning library finished")

    def onScanStarted(self, *arg):
        self.logger.debug("Scanning library started")

    def onScanFinished(self, *arg):
        self.logger.debug("Scanning library finished")

    def onScreensaverActivated(self, *arg):
        self.logger.debug("Screensaver activated")
        self.clientsocket.sendEvents(EVENT.KODI_SCREENSAVER_ACTIVATED)

    def onScreensaverDeactivated(self, *arg):
        self.logger.debug("Screensaver deactivated")
        self.clientsocket.sendEvents(EVENT.KODI_SCREENSAVER_DEACTIVATED)
        

    def onDPMSActivated(self, *arg):
        self.logger.debug("DPMS activated")

    def onDPMSDeactivated(self, *arg):                                           
        self.logger.debug("DPMS deactivated")   

class KodiPlayer(xbmc.Player):
    
    def __init__ (self):
        xbmc.Player.__init__(self)
        self.logger = None

    def onPlayBackStarted(self, *arg):
        self.logger.debug("Playback started")
        self.clientsocket.sendEvents(EVENT.KODI_PLAYBACK_STARTED)

    def onPlayBackPaused(self, *arg):
        self.logger.debug("Playback paused")
        self.clientsocket.sendEvents(EVENT.KODI_PLAYBACK_PAUSED)

    def onPlayBackResumed(self, *arg):
        self.logger.debug("Playback resumed")
        self.clientsocket.sendEvents(EVENT.KODI_PLAYBACK_RESUMED)

    def onPlayBackStopped(self, *arg):
        self.logger.debug("Playback stopped")
        self.clientsocket.sendEvents(EVENT.KODI_PLAYBACK_STOPPED)

    def onPlayBackEnded(self, *arg):
        self.logger.debug("Playback ended")
        self.clientsocket.sendEvents(EVENT.KODI_PLAYBACK_ENDED)

#xbmc.executebuiltin("Action(contextmenu)")

def wakeUpKodi():
    #pass
    xbmc.executebuiltin('CECActivateSource')
    

            
eventhandler = { EVENT.CECLOG_ACTIVESOURCE_OSMC:          wakeUpKodi,
                # EVENT.CECLOG_ACTIVESOURCE_CHROMECAST:    aaa,
                # EVENT.CECLOG_ACTIVESOURCE_PLAYSTATION_4: bbb,
               }

def receiver(data, addr):
    ##########
    ## events
    #
    if EVENT.TAG in data.keys():
        for event in data[EVENT.TAG]:
            print("Received event: %s" % str(event))

            if event in eventhandler.keys():
                eventhandler[event]()


if __name__ == '__main__':
    logging.basicConfig(format=CFG.LOG_FORMAT, filename=LOG_FILE, level=logging.DEBUG)
    logger = logging.getLogger(APP_NAME)


    clientbroadcast = communicator.SocketClient((communicator.BROADCAST_HOST, CFG.SOCKET_UDP_PORT), communicator.SOCKET_UDP)
    clientbroadcast.keepAlive(False)
    clientbroadcast.useReplying(False)
    clientbroadcast.initClient()

    clientsocket = communicator.SocketClient(CFG.SOCKET_UNIX_FILE, communicator.SOCKET_TCP)
    clientsocket.keepAlive(True)
    clientsocket.useReplying(False)
    clientsocket.setDataHandler(receiver)
    clientsocket.initClient()
    clientsocket.startReceiving()
    
    player = KodiPlayer()
    player.logger = logger
    player.clientsocket = clientbroadcast

    monitor = KodiMonitor()
    monitor.logger = logger
    monitor.clientsocket = clientbroadcast
    
    dialog = xbmcgui.Dialog()
    dialog.notification(APP_NAME, "I'm ready!")

    while not xbmc.Monitor().abortRequested():
        #self.logger.debug("Running")
        xbmc.sleep(5000)
