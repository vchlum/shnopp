#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import datetime
import time

from config import CFG

try:
    import astral
except ImportError:
    raise Exception('Importing astral failed!')



class DayTime(object):
    """
    day time checker - is night or twilight or sun is shnining?
    """

    def __init__(self, place = CFG.LOCATION):
        """
        init function
        :param place: string with current place/position
        """
        
        self.place = place
        self.checked = None
        self.dawn = 0
        self.sunrise = 0
        self.sunset = 0
        self.dusk = 0
        self.checkTime()

    def checkTime(self):
        """
        use google to check the sun position time of day
        """
        
        # check only if neccessary
        if self.checked and self.checked == time.strftime("%j"):
            return self.checked

        try:
            a = astral.Astral(astral.GoogleGeocoder)
            a.solar_depression = 'civil'

            city = a[self.place]

            self.dawn    = int(city.sun(date=datetime.date.today(), local=True)['dawn'].strftime('%s'))
            self.sunrise = int(city.sun(date=datetime.date.today(), local=True)['sunrise'].strftime('%s'))
            self.sunset  = int(city.sun(date=datetime.date.today(), local=True)['sunset'].strftime('%s'))
            self.dusk    = int(city.sun(date=datetime.date.today(), local=True)['dusk'].strftime('%s'))

        except Exception as err:
            self.checked = None
            self.checked = str(err)
            self.dawn = 1
            self.dusk = 2
            self.sunrise = 3
            self.sunset = 4

        else:
            self.checked = time.strftime("%j")

        return self.checked

    def isShining(self):
        """
        check if sun is shining
        """
         
        now = time.time()

        if self.checkTime():
            return self.sunrise <= now and now < self.sunset

        return True # default is yes 

    def isTwilight(self):
        """
        check twilight
        """
        
        now = time.time()

        if self.checkTime():
            return (self.dawn <= now and now < self.sunrise) or \
                   (self.sunset <= now and now < self.dusk)

        return False # default is no
 
    def isDarkness(self):
        """
        check night
        """
        
        now = time.time()   
     
        if self.checkTime():
            return self.dusk <= now or now < self.sunrise

        return False # default is no
