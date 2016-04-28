#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from config import CMD

LEFT_BOTTOM  = "Levá spodní"
RIGHT_BOTTOM = "Pravá spodní"
LEFT_TOP     = "Levá vrchní"
RIGHT_TOP    = "Pravá vrchní"
BOTTOM       = "Spodní řada"
TOP          = "Vrchní řada"
ALL          = "Vše"



OUTPUT_4   = 4
OUTPUT_5   = 5
OUTPUT_6   = 6
OUTPUT_7   = 7

OUTPUT_ALL               = [OUTPUT_4, OUTPUT_5, OUTPUT_6, OUTPUT_7]
OUTPUT_BOTTOM            = [OUTPUT_4, OUTPUT_5]
OUTPUT_TOP               = [OUTPUT_6, OUTPUT_7]
OUTPUT_CLOCKWISE         = [OUTPUT_4, OUTPUT_6, OUTPUT_7, OUTPUT_5]
OUTPUT_COUNTER_CLOCKWISE = list(reversed(OUTPUT_CLOCKWISE))



PIFACE_LED =   {"Obývák":{"TV stěna": {"Podsvícení":{ 
                 LEFT_BOTTOM:  {CMD.ON: OUTPUT_4,      CMD.OFF: OUTPUT_4,      CMD.TOGGLE: OUTPUT_4},
                 RIGHT_BOTTOM: {CMD.ON: OUTPUT_5,      CMD.OFF: OUTPUT_5,      CMD.TOGGLE: OUTPUT_5},
                 LEFT_TOP:     {CMD.ON: OUTPUT_6,      CMD.OFF: OUTPUT_6,      CMD.TOGGLE: OUTPUT_6},
                 RIGHT_TOP:    {CMD.ON: OUTPUT_7,      CMD.OFF: OUTPUT_7,      CMD.TOGGLE: OUTPUT_7},

                 BOTTOM:       {CMD.ON: OUTPUT_BOTTOM, CMD.OFF: OUTPUT_BOTTOM, CMD.TOGGLE: OUTPUT_BOTTOM},
                 TOP:          {CMD.ON: OUTPUT_TOP,    CMD.OFF: OUTPUT_TOP,    CMD.TOGGLE: OUTPUT_TOP},

                 ALL:          {CMD.ON: OUTPUT_ALL,    CMD.OFF: OUTPUT_ALL,    CMD.TOGGLE: OUTPUT_ALL},
}}}}

ITEMS              = PIFACE_LED

