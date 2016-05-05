#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
import subprocess, re

global MY_DEVICE
MY_DEVICE="SC-NP10"
BT_DEVICES = {"SC-NP10":"00:0B:97:17:3F:09"}

dialog = xbmcgui.Dialog()

def bt_command(command, device):
    comm='echo " %s %s\nquit" | bluetoothctl' % (command, BT_DEVICES[device])
    process = subprocess.Popen(comm, shell=True, stdout=subprocess.PIPE)
    out = process.communicate()[0]
    return out

def bt_connect(device):
    out = bt_command("info", device)
    for line in out.split("\n"):
        if re.match("\s*Connected:\s*yes\s*", line):
            return
    dialog.notification(device, "Pripojuji BT...")
    bt_command("connect", device)

def bt_disconnect(device):
    bt_command("disconnect", device)

class KodiMonitor(xbmc.Monitor):
    
    def __init__ (self):          
        xbmc.Monitor.__init__(self)

    def onScreensaverActivated(self, *arg):
        bt_disconnect(MY_DEVICE)

    def onScreensaverDeactivated(self, *arg):
        bt_connect(MY_DEVICE)

    def onDPMSActivated(self, *arg):
        bt_disconnect(MY_DEVICE)

    def onDPMSDeactivated(self, *arg):                                           
        bt_connect(MY_DEVICE) 

class KodiPlayer(xbmc.Player):
    
    def __init__ (self):
        xbmc.Player.__init__(self)

    def onPlayBackStarted(self, *arg):
        bt_connect(MY_DEVICE)

    def onPlayBackPaused(self, *arg):
        pass

    def onPlayBackResumed(self, *arg):
        bt_connect(MY_DEVICE)

    def onPlayBackStopped(self, *arg):
        pass

    def onPlayBackEnded(self, *arg):
        pass

if __name__ == '__main__':

    player = KodiPlayer()
    monitor = KodiMonitor()
    
    xbmc.sleep(5000)
    bt_connect(MY_DEVICE)
    
    while not xbmc.Monitor().abortRequested():
        xbmc.sleep(5000)
