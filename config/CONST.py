#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import os

HOSTNAME = os.uname()[1]

APP_NAME = "SmartHomeNotOnlyPiPowered u Váši"
APP_SHORT_NAME = "shnopp"
DESCRIPTION = ""
AUTHORS = ["Vaclav Chlumsky <chlumskyvaclav@gmail.com>"]
VERSION = "0.51~alfa"
COPYRIGHT = "(C) 2016 Vaclav Chlumsky"

DELIMITER = "::"

# neni finalni, upravit, opravit...
RET_OK = 0
RET_ERROR = 1
RET_IO_ERROR = 100
