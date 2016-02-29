#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket

POWEROFF = "Vypnout"
REBOOT   = "Restart"
SYSTEM_TAG   = "Dostupné systémy"

SYSTEM =   {socket.gethostname(): {
                 POWEROFF:  "sudo /sbin/shutdown -P now",
                 REBOOT:  "sudo /sbin/shutdown -r now",
}}

ITEMS              = SYSTEM

