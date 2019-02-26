#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys

from misc import logger
from misc import plugin

from config import CFG

# http://webpy.org
import web



class Plugin(plugin.Plugin):
    """
    web gui plugin - http web page 
    """

    urls = (
        '/', 'index',
        )
    
    class index:
        """
        web url
        """
        def GET(self):
            return "none"

        def POST(self):
            """
            post
            """
            global items
            
            try:
                input = web.input()
                if 'pwd' in input.keys() and input['pwd'] == CFG.WEB_HOOK_PASSWORD:
                    logger.logDebug("password ok")
                    if 'action' in input.keys() and input['action'] in items.keys():
                        if len(items[input['action']]) > 0:
                            sendEvents(items[input['action']])
                            return "ok"
                    else:
                        logger.logDebug("wrong action")
                else:
                    logger.logDebug("wrong password")

            except Exception as err:
                logger.logError(str(err))                  
            return "none"



    def init(self):
        """
        initialize
        """
                
        self.items = CFG.ITEMS_WEB_HOOK

    def run(self):
        """
        plugin main
        """
                
        try:
            sys.argv = [sys.argv[0], str(CFG.WEB_HOOK_PORT)]

            fvars = globals()

            # manual inheritance
            for i in [attr for attr in dir(self) if not callable(attr) and not attr.startswith("__")]:
                fvars[i] = eval('self.' + i)
                 
            web_app = web.application(self.urls, fvars)
            web_app.internalerror = web.debugerror
            web_app.run()
        except Exception as err:
            logger.logError("error starting web: %s" % err )
              
