#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys
import os
import time

from misc import logger
from misc import plugin

from config import CONST
from config import METHOD
from config import CFG

# http://webpy.org
import web



class Plugin(plugin.Plugin):
    """
    web gui plugin - http web page 
    """

    urls = (
        '/(js|css|img)/(.+\.js|.+\.png)', 'static',
        '/', 'index',
        '/action/(.+)', 'action'
        )
    
    render = web.template.render(os.path.join(os.path.dirname(__file__), 'gui_web_templates/'), base='base')
    
    class static:
        """
        web url
        """
                
        def GET(self, media, filename):
            """
            get
            """
                        
            try:
                workingdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gui_web_templates")
                fullfilename = os.path.join(workingdir, media, filename)
                f = open(fullfilename, 'r')
                return f.read()
                
            except Exception as err:
                logger.logError(str(err))
                return ''

    class index:
        """
        web url
        """
        
        buttons = {}
        
        global render
        
        form = web.form.Form(
            web.form.Button(u'\u21BB'),
            )

        def GET(self):
            """
            get
            """
            
            global items
            
            form = self.form()
            self.buttons={}
            self.getforms("", items)
            
            keys_friendly_name = {}
            for i in self.buttons.keys():
                keys_friendly_name[i] = (" - ").join(i.split(CONST.DELIMITER)[1:])

            # sort buttons by second column
            sorted_buttons = [CONST.DELIMITER.join(y) for y in sorted([x.split(CONST.DELIMITER) for x in sorted(self.buttons.keys())], key = lambda x: x[1])]

            return render.index(CONST.APP_NAME, sorted_buttons, self.buttons, keys_friendly_name, form)

        def POST(self):
            """
            post
            """
            
            form = self.form()
            if not form.validates():
                # asi k nicemu
                return render.index({}, form)
            raise web.seeother('/')

        def getforms(self, path, data):
            """
            recursively process items, prepare buttons
            :param path:
            :param data:
            """
            
            for i in data:
                if isinstance(data[i], dict):
                    new_p = path
                    if len(path)>0:
                        new_p = path + CONST.DELIMITER
                    self.getforms(new_p + i, data[i])
                else:
                    if path in self.buttons.keys():
                        if i not in self.buttons[path]:
                            self.buttons[path].append(i)
                    else:
                        self.buttons[path]=[i]

    class action:
        """
        web url
        """

        def POST(self, id):
            """
            post
            """
            
            id=id.encode('utf-8')
            if (str(id) == "askForItems"):
                global items
                items.clear()
                askForItems()
                time.sleep(2)
                
            id = id + CONST.DELIMITER + web.data().encode('utf-8').split("=")[1]
            
            target = id.split(CONST.DELIMITER)[0]
            cmdstring = CONST.DELIMITER.join(id.split(CONST.DELIMITER)[1:])
        
            logger.logDebug("Sending cmd for %s: '%s'" % (target, cmdstring) )
            sendCommands([cmdstring], target)

            raise web.seeother('/')

    def init(self):
        """
        initialize
        """
                
        self.items = {}

    def run(self):
        """
        plugin main
        """
                
        try:
            sys.argv = [sys.argv[0], str(CFG.PORT)]

            fvars = globals()

            # manual inheritance
            for i in [attr for attr in dir(self) if not callable(attr) and not attr.startswith("__")]:
                fvars[i] = eval('self.' + i)
                 
            web_app = web.application(self.urls, fvars)
            web_app.internalerror = web.debugerror
            web_app.run()
        except Exception as err:
            logger.logError("error starting web: %s" % err )
                    
    def receiveData(self, data_dict):
        """
        handle received data
        :param data_dict: received data
        """                
        
        if "result" in data_dict.keys():
            if data_dict["result"]["type"] == METHOD.ITEMS:
                target = data_dict["result"]["plugin"]
                if not target in self.items:
                    self.items[target] = {}    
     
                self.items[target].update(data_dict["result"]["items"])