#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from config import CONST



### general about ###

OWNER_NAME = "Váša"
OWNER_EMAIL = "chlumskyvaclav@gmail.com"
LOCATION = "Brno"



### general ###

DIR_RUN = "/tmp/" + CONST.APP_SHORT_NAME + "/"
DIR_VAR = "/tmp/" + CONST.APP_SHORT_NAME + "/"

PID_FILE = DIR_RUN + CONST.APP_SHORT_NAME.lower() + ".pid"



### socket ###

SOCKET_TCP_ENABLED = True
SOCKET_TCP_HOSTNAME = ""
SOCKET_TCP_PORT = 54862
SOCKET_TCP_ENABLE_REPLY = True

SOCKET_UDP_ENABLED = True
SOCKET_UDP_HOSTNAME = ""
SOCKET_UDP_PORT = 54863
SOCKET_UDP_ENABLE_REPLY = False

SOCKET_UNIX_ENABLED = True
SOCKET_UNIX_FILE = DIR_RUN + CONST.APP_SHORT_NAME.lower() + ".sock"
SOCKET_UNIX_ENABLE_REPLY = True



### loging ###

LOG_FILE = DIR_VAR + CONST.APP_SHORT_NAME.lower() + ".log"
#LOG_FORMAT = "%(asctime)s %(name)s [%(levelname)s] %(message)s"
LOG_FORMAT = "%(asctime)s %(name)s %(message)s"
#LOG_LEVEL = logging.DEBUG
