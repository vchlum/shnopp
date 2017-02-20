#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket

POWEROFF = "Vypnout"
REBOOT   = "Restart"
RESTART_KODI   = "RestartKODI"
SYSTEM_TAG   = "Dostupné systémy"

SYSTEM =   {socket.gethostname(): {
                 POWEROFF:  "sudo /sbin/shutdown -P now",
                 REBOOT:  "sudo /sbin/shutdown -r now",
                 RESTART_KODI:  "sudo /bin/systemctl restart mediacenter",
}}

ITEMS              = SYSTEM

