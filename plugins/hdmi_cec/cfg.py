#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from config import CMD
from config import CONST

EMIT_REMOTECONTROL_KEYS = False
CEC_LOG_TO_DEFAULT_LOG = False

CEC_DEV1="TV"
CEC_DEV2=CONST.HOSTNAME[:12]
CEC_DEV3="PlayStation 4"
CEC_DEV4="GoogleCast"

CEC_THIS_DEV=CEC_DEV2

ITEMS_CMD = {CMD.POWERON: None, CMD.STANDBY: None}

CEC_DEV =  {"Obývák": {"TV stěna": {
            CEC_DEV1: ITEMS_CMD,
            CEC_DEV2: ITEMS_CMD,
            CEC_DEV3: ITEMS_CMD,
            CEC_DEV4: ITEMS_CMD, 
}}}

ITEMS              = CEC_DEV


