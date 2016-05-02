#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys
import os

from misc import logger
from misc import plugin

from config import CONST
from config import METHOD

import cfg

import web



####################################################################
####################################################################
####################################################################
### WEB interface pluggin                                        ###
####################################################################
####################################################################
####################################################################

############################################
### plugin main class                    ###
############################################
############################################
############################################

class Plugin(plugin.Plugin):

    urls = (
        '/(js|css|img)/(.+\.js|.+\.png)', 'static',
        '/', 'index',
        '/action/(.+)', 'action'
        )
    
    render = web.template.render(os.path.join(os.path.dirname(__file__), 'gui_web_templates/'), base='base')
    
    class static:
        def GET(self, media, filename):
            try:
                workingdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gui_web_templates")
                fullfilename = os.path.join(workingdir, media, filename)
                f = open(fullfilename, 'r')
                return f.read()
                
            except Exception as err:
                logger.logError(str(err))
                return ''

    #########################
    ###
    #    
    class index:
        
        buttons = {}
        
        global render
        
        form = web.form.Form(
            web.form.Button(u'\u21BB'),
            )

        ##########
        ##
        #        
        def GET(self):
            global items
            
            form = self.form()
            self.buttons={}
            self.getforms("", items)
            
            keys_friendly_name = {}
            for i in self.buttons.keys():
                keys_friendly_name[i] = (" - ").join(i.split(CONST.DELIMITER)[1:])
                
            
            return render.index(CONST.APP_NAME, sorted(self.buttons.keys()), self.buttons, keys_friendly_name, form)

        ##########
        ##
        #
        def POST(self):
            form = self.form()
            if not form.validates():
                # asi k nicemu
                return render.index({}, form)
            raise web.seeother('/')

        ##########
        ##
        #        
        def getforms(self, path, data):
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

    #########################
    ###
    #        
    class action:
        
        ##########
        ##
        #        
        def POST(self, id):
            id=id.encode('utf-8')
            if (str(id) == "askForItems"):
                askForItems()
                
            id = id + CONST.DELIMITER + web.data().encode('utf-8').split("=")[1]
            print str(id) 
            
            target = id.split(CONST.DELIMITER)[0]
            cmdstring = CONST.DELIMITER.join(id.split(CONST.DELIMITER)[1:])
        
            logger.logDebug("Sending cmd for %s: '%s'" % (target, cmdstring) )
            sendCommands([cmdstring], target)

            raise web.seeother('/')

    #########################
    ###
    #
    def init(self):
        self.items = {}

    #########################
    ###
    #
    def run(self):
        try:
            sys.argv = [sys.argv[0], str(cfg.PORT)]

            fvars = globals()

            # rucne podedim
            for i in [attr for attr in dir(self) if not callable(attr) and not attr.startswith("__")]:
                fvars[i] = eval('self.' + i)
                 
            web_app = web.application(self.urls, fvars)
            web_app.internalerror = web.debugerror
            web_app.run()
        except Exception as err:
            logger.logError("error starting web: %s" % err )
                    
    #########################
    ###
    #
    def receiveData(self, data_dict):        
        
        if "result" in data_dict.keys():
            if data_dict["result"]["type"] == METHOD.ITEMS:
                target = data_dict["result"]["plugin"]
                if not target in self.items:
                    self.items[target] = {}                
                self.items[target].update(data_dict["result"]["items"])