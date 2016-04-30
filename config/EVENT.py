import os

from config import CONST

TAG = "event"

### personal ###

PERSONAL_TIME_TO_WAKEUP = "personal time-to-wakeup"
PERSONAL_TIME_TO_SLEEP  = "personal time-to-sleep"

### cec ###

CECLOG_ACTIVESOURCE_TEMPLATE =          "ceclog-activesource" + CONST.DELIMITER + "%s"
CECLOG_ACTIVESOURCE_OSMC =              CECLOG_ACTIVESOURCE_TEMPLATE % os.uname()[1][:12]
CECLOG_ACTIVESOURCE_CHROMECAST =        CECLOG_ACTIVESOURCE_TEMPLATE % "Chromecast"
CECLOG_ACTIVESOURCE_PLAYSTATION_4 =     CECLOG_ACTIVESOURCE_TEMPLATE % "PlayStation 4"

CEC_ACTIVESOURCE_TEMPLATE =          "cec-activesource" + CONST.DELIMITER + "%s"
CEC_ACTIVESOURCE_OSMC =              CEC_ACTIVESOURCE_TEMPLATE % os.uname()[1][:12]
CEC_ACTIVESOURCE_CHROMECAST =        CEC_ACTIVESOURCE_TEMPLATE % "Chromecast"
CEC_ACTIVESOURCE_PLAYSTATION_4 =     CEC_ACTIVESOURCE_TEMPLATE % "PlayStation 4"

CEC_KEYRELEASED_TEMPLATE = "cec-keyreleased" + CONST.DELIMITER + "%i" + CONST.DELIMITER + "%i"
           
### kodi ###
          
KODI_PLAYBACK_STARTED =                 "kodi playback started"
KODI_PLAYBACK_PAUSED =                  "kodi playback paused"
KODI_PLAYBACK_RESUMED =                 "kodi playback resumed"
KODI_PLAYBACK_STOPPED =                 "kodi playback stoped"
KODI_PLAYBACK_ENDED =                   "kodi playback ended"
                     
KODI_SCREENSAVER_ACTIVATED =            "kodi screensaver activated"
KODI_SCREENSAVER_DEACTIVATED =          "kodi screensaver deactivated"
