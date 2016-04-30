#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import os

from config import CMD

EMIT_REMOTECONTROL_KEYS = False

CEC_DEV1="TV"
CEC_DEV2=os.uname()[1][:12]
CEC_DEV3="PlayStation 4"
CEC_DEV4="Chromecast"

CEC_THIS_DEV=CEC_DEV2



CEC_DEV =  {"Obývák": {"TV stěna": { CEC_DEV1:  {CMD.POWERON: None, CMD.STANDBY: None},
              CEC_DEV2:  {CMD.POWERON: None, CMD.STANDBY: None},
              CEC_DEV3:  {CMD.POWERON: None, CMD.STANDBY: None},
              CEC_DEV4:  {CMD.POWERON: None, CMD.STANDBY: None}, 
}}}

ITEMS              = CEC_DEV

CEC_LOG_TO_DEFAULT_LOG = 0
