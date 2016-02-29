#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import uinput
import re
import os

from misc import logger
from misc import plugin

from config import CONST
from config import CMD
from config import EVENT
from config import REQ

import cfg

try:
    import cec
except ImportError:
    raise Exception('Importing cec failed!')



####################################################################
####################################################################
####################################################################
### plugin for hdmi-cec devices TV                               ###
####################################################################
####################################################################
####################################################################



############################################
### plugin main class                    ###
############################################
############################################
############################################

class Plugin(plugin.Plugin):
    keymap = {
        0:   uinput.KEY_ENTER,
        1:   uinput.KEY_UP,
        2:   uinput.KEY_DOWN,
        3:   uinput.KEY_LEFT,
        4:   uinput.KEY_RIGHT,
        13:  uinput.KEY_BACK,
        68:  uinput.KEY_PLAY,
        69:  uinput.KEY_STOP,
        70:  uinput.KEY_PAUSE,
        75:  uinput.KEY_FASTFORWARD,
        76:  uinput.KEY_REWIND,
        113: uinput.KEY_BLUE,
        114: uinput.KEY_RED,
        115: uinput.KEY_YELLOW,
        116: uinput.KEY_GREEN,
    }

    ######################################
    # cec-device subclass                # 
    ######################################
    class Device(object):
        iAddress = None
        osdName = None
        vendorId = None
        cecVersion = None
        physicalAddress = None        
        power = None
        active = None        
        libCEC = None
        
        ##########
        ##
        #
        def __init__(self, iAddress, libCEC):
            self.iAddress = iAddress
            self.libCEC = libCEC
            self.detectDevice()
            
        ##########
        ##
        #
        def detectDevice(self):
            try:
                self.osdName         = self.libCEC.GetDeviceOSDName(self.iAddress)
                self.vendorId        = self.libCEC.GetDeviceVendorId(self.iAddress)
                self.cecVersion      = self.libCEC.GetDeviceCecVersion(self.iAddress)
                self.physicalAddress = self.libCEC.GetDevicePhysicalAddress(self.iAddress)
                self.power           = self.libCEC.GetDevicePowerStatus(self.iAddress)
                self.active          = self.libCEC.IsActiveSource(self.iAddress)    
            except Exception as err:
                raise Exception("Detecting CEC device error: %s" % str(err) )
         
        ##########
        ##
        #   
        def getOsdName(self):
            return self.osdName
        
        ##########
        ##
        #
        def getVendor(self):
            return self.vendorId
        
        ##########
        ##
        #
        def getVendorString(self):
            return self.libCEC.VendorIdToString(self.vendorId)

        ##########
        ##
        #
        def getCecVersion(self):
            return self.cecVersion
        
        ##########
        ##
        #
        def getCecVersionString(self):
            return self.libCEC.CecVersionToString(self.cecVersion)              
         
        ##########
        ##
        #       
        def getPhysicalAddress(self):
            return self.physicalAddress
        
        ##########
        ##
        #
        def getPowerStatus(self):
            return self.libCEC.GetDevicePowerStatus(self.iAddress)
        
        ##########
        ##
        #
        def getPowerString(self):
            return self.libCEC.PowerStatusToString(self.getPowerStatus())
        
        ##########
        ##
        #
        def isActiveSource(self):
            return self.libCEC.IsActiveSource(self.iAddress)
        
        ##########
        ##
        #
        def isActiveDevice(self):
            return self.libCEC.IsActiveDevice(self.iAddress)

        ##########
        ##
        #
        def poweronDevice(self):
            return self.libCEC.PowerOnDevices(self.iAddress)
        
        ##########
        ##
        #
        def standbyDevice(self):
            return self.libCEC.StandbyDevices(self.iAddress)

    #########################
    ###
    #
    def init(self):
        self.items = cfg.ITEMS
        self.libCEC = {}
        self.uidevice = uinput.Device(self.keymap.values())
        self.cecconfig = cec.libcec_configuration()
        self.this_cec_name = os.uname()[1]
        self.devices = {}

        self.autoinit = True
        if self.autoinit:
            self.initConfig(self.this_cec_name)
            self.initDefaultCB()
            self.initlibCEC()
            self.detectDevices()

    #########################
    ###
    #
    def __getitem__(self, key):
        if not key in self.getDevices():
            self.detectDevices()
            
        if key in self.getDevices():
            return self.devices[key]
        
        return None
    
    #########################
    ###
    #
    def initConfig(self, this_cec_name):
        logger.logDebug("Initializing libCEC config")

        try:
            self.cecconfig.strDeviceName = self.this_cec_name
            # 0 = do not make the primary device the active source 
            self.cecconfig.bActivateSource = 0
            # https://github.com/Pulse-Eight/libcec/blob/2c675dac48387c48c7f43c5d2547ef0c4ef5c7dd/include/cectypes.h
            #self.cecconfig.bMonitorOnly = 1
            self.cecconfig.deviceTypes.Add(cec.CEC_DEVICE_TYPE_RECORDING_DEVICE)
            self.cecconfig.clientVersion = cec.LIBCEC_VERSION_CURRENT
        except Exception as err:
            logger.logError("Initializing libCEC config error: %s" % str(err) )

    #########################
    ###
    #
    def initDefaultCB(self):
        logger.logDebug("Settings CEC default callbacks")
        self.setLogCallback(self.cecLogCallback)
        self.setKeyPressCallback(self.cecKeyPressCallback)
        self.setCommandCallback(self.cecCommandCallback)    
        self.setMenuStateCallback(self.cecMenuStateCallback)
        self.setSourceActivatedCallback(self.cecSourceActivatedCallback)

    #########################
    ###
    #
    # detect an adapter and return the com port path
    def detectAdapter(self):
        logger.logDebug("Detecting CEC adapters")

        try:
            adapter_found = None
            adapters = self.libCEC.DetectAdapters()

            for adapter in adapters:
                logger.logInfo("CEC adapter found on port: %s vendor: %s product: %s" % (adapter.strComName, hex(adapter.iVendorId), hex(adapter.iProductId)))
                adapter_found = adapter.strComName

            return adapter_found

        except Exception as err:
            logger.logError("Detecting CEC adapter error: %s" % str(err) )
            return None

    #########################
    ###
    #
    def initlibCEC(self):
            try:
                self.libCEC = cec.ICECAdapter.Create(self.cecconfig)
            except Exception as err:
                logger.logError("Creating CEC adapter error: %s" % str(err) )

            adapter = self.detectAdapter()

            if adapter == None:
                logger.logInfo("No CEC adapters found")
            else:
                if self.libCEC.Open(adapter):
                    logger.logInfo("CEC connection opened")
                else:
                    logger.logInfo("Failed to open a connection to the CEC adapter")

    #########################
    ###
    #
    def detectDevices(self):
        logger.logDebug("Detecting CEC devices")

        try:
            self.libCEC.RescanActiveDevices()
            addresses = self.libCEC.GetActiveDevices()
            activeSource = self.libCEC.GetActiveSource()

            for iAddress in range(0, 15):
                if addresses.IsSet(iAddress):
                    self.devices[self.libCEC.GetDeviceOSDName(iAddress)] = self.Device(iAddress, self.libCEC)
                    logger.logInfo("CEC device %s detected on address: %i" % (self.libCEC.GetDeviceOSDName(iAddress), iAddress) )

        except Exception as err:
            logger.logError("Detecting CEC devices error: %s" % str(err) )

    ######################################
    # cec-commands                       # 
    ######################################
     
    #########################
    ###
    #   
    def standby(self):
        return self.libCEC.StandbyDevices()                
     
    #########################
    ###
    #   
    def setActiveSource(self):
        return self.libCEC.SetActiveSource()
     
    #########################
    ###
    #   
    def setInactive(self):
        return self.libCEC.SetInactiveView()
    
    #########################
    ###
    #
    def getActiveSource(self):
        return self.libCEC.GetActiveSource()
    
    #########################
    ###
    #
    def getActiveSourceOsdName(self):
        return self.libCEC.GetDeviceOSDName(self.getActiveSource())
    
    #########################
    ###
    #
    def getDeviceOSDName(self, iAddress):
        return self.libCEC.GetDeviceOSDName(iAddress)
    
    #########################
    ###
    #
    def getDevices(self):
        return self.devices.keys()
    
    #########################
    ###
    #
    def poweronDevice(self, devicename):
        if devicename == cfg.CEC_THIS_DEV:
            self["TV"].poweronDevice()
            self.setActiveSource()            
            
        if self[devicename]:            
             self[devicename].poweronDevice()
     
    #########################
    ###
    #        
    def standbyDevice(self, devicename):
        if devicename == cfg.CEC_THIS_DEV:
            self.setInactive()   
            self.standby()
            
        if self[devicename]:
             self[devicename].standbyDevice()
          

    ######################################
    # cec-callbacks                      # 
    ######################################

    #########################
    ###
    #
    def setLogCallback(self, callback):
        self.cecconfig.SetLogCallback(callback)
        
    #########################
    ###
    #
    def setKeyPressCallback(self, callback):
        self.cecconfig.SetKeyPressCallback(callback)
     
    #########################
    ###
    #   
    def setCommandCallback(self, callback):
        self.cecconfig.SetCommandCallback(callback)
     
    #########################
    ###
    #   
    def setMenuStateCallback(self, callback):
        self.cecconfig.SetMenuStateCallback(callback)
       
    #########################
    ###
    # 
    def setSourceActivatedCallback(self, callback):
        self.cecconfig.SetSourceActivatedCallback(callback)
   
    #########################
    ###
    #
    def cecLogCallback(self, level, timestamp, message):
        libCECloglevel_dict = {cec.CEC_LOG_ERROR:   "ERROR",
                               cec.CEC_LOG_WARNING: "WARNING",
                               cec.CEC_LOG_NOTICE:  "NOTICE",
                               cec.CEC_LOG_TRAFFIC: "TRAFFIC",
                               cec.CEC_LOG_DEBUG:   "DEBUG",
                              }

        if hasattr(cfg, 'CEC_LOG_TO_DEFAULT_LOG') and cfg.CEC_LOG_TO_DEFAULT_LOG:
            logger.logDebug("[CEC_LOG_%s] %s %s" % (libCECloglevel_dict[level], str(timestamp), message))

        if level == cec.CEC_LOG_DEBUG:

            pattern_active_source = "^making .* \((.+?)\) the active source$"
            m_active_source = re.search(pattern_active_source, message)

            if m_active_source:
                iAddress = int(m_active_source.group(1), 16)
                osdName = self.getDeviceOSDName(int(iAddress))
                logger.logInfo("Source %s is active" % osdName)

                try:
                    self.sendEvents(EVENT.CECLOG_ACTIVESOURCE_TEMPLATE % osdName)
                except Exception as err:
                    logger.logError("error %s" % str(err))
                    
        return RET_OK
    
    #########################
    ###
    #
    def cecKeyPressCallback(self, keycode, duration):
        if duration == 0:
            logger.logDebug("[KEY] %s pressed, time: %s" % (str(keycode), str(duration)))

        if duration > 0:
            logger.logDebug("[KEY] %s released, time: %s" % (str(keycode), str(duration)))

            self.sendEvents(EVENT.CEC_KEYRELEASED_TEMPLATE % (keycode, duration))

            if keycode in self.keymap.keys():
                uidevice.emit_click(self.keymap[keycode])
                logger.logDebug("[KEY] code %s emitted" % str(self.keymap[keycode]))

        return RET_OK

    #########################
    ###
    #
    def cecCommandCallback(self, cmd):
        logger.logDebug("[COMMAND] %s" % cmd)
        return RET_OK

    #########################
    ###
    #
    def cecMenuStateCallback(self, state):
        logger.logDebug("[MENUSTATE] %s" % str(state))
        return RET_OK

    #########################
    ###
    #
    def cecSourceActivatedCallback(self, logicalAddress, activated):
        logger.logDebug("[SOURCEACTIVATED] %s:%s active source: %s" % (str(logicalAddress), str(activated), cec_lib.GetActiveSourceOsdName()))
        self.sendEvents(EVENT.CEC_ACTIVESOURCE_TEMPLATE % str(activated))
        return RET_OK

    ######################################
    # event specific functions           # 
    ######################################
    
    #########################
    ###
    #    
    def poweronThisDev(self):
        self.poweronDevice(cfg.CEC_THIS_DEV)
        self["TV"].poweronDevice()
        self.setActiveSource()
        
    #########################
    ###
    #          
    def standbyIfNobodyElse(self):

        for device in self.getDevices():
            if device != cfg.CEC_THIS_DEV and self[device].isActiveSource():
                return # if somebody else is active dont poweroff

        self.setInactive()
        self["TV"].standbyDevice()

    #########################
    ###
    #          
    def standbyAllAnyway(self):
        self.setInactive()

        for device in self.getDevices():
            self[device].standbyDevice()
        

    ######################################
    # receiver and received cmd handlers # 
    ######################################

    cmdhandler = { CMD.POWERON: poweronDevice,
                   CMD.STANDBY: standbyDevice,
                  }
    
    eventhandler = { EVENT.KODI_PLAYBACK_STARTED: poweronThisDev,
                     EVENT.KODI_PLAYBACK_RESUMED: poweronThisDev,
                     
                     EVENT.KODI_SCREENSAVER_ACTIVATED:   standbyIfNobodyElse,

                     EVENT.PERSONAL_TIME_TO_SLEEP: standbyAllAnyway,
                   }    
    
    #########################
    ###
    #
    # example:  mydata  = '{"cmd":{"PlayStation 4:poweron", "TV:poweron"}}'
    def receiveData(self, data, mydata):
        logger.logDebug("Received data: '%s'" % str(data))
        
        ##########
        ## data for me
        # 
        if mydata:
            if CMD.TAG in mydata.keys():
                for cmdstring in mydata[CMD.TAG]:
                    try:                  

                        [item, command] = cmdstring.split(CONST.DELIMITER)[-2:]
                        
                        self.cmdhandler[command](self, item)
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
