#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import pkgutil
import sys
import os
import threading

from misc import logger
from misc import plugin

from config import CONST
from config import METHOD

if len( os.getenv( 'DISPLAY', '' ) ) == 0:
    os.putenv( 'DISPLAY', ':0.0' )
            
import gtk
gtk.gdk.threads_init()



class Plugin(plugin.Plugin):
    """
    gtk gui plugin - systry menu 
    """
    
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
            self.systray = gtk.StatusIcon()
            self.systray.set_from_stock(gtk.STOCK_ABOUT)
            self.systray.connect('popup-menu', self.onRightClick)
            gtk.main()
        except Exception as err:
            logger.logDebug("error: %s", err )
            
        self.askForItems()

    def onRightClick(self, icon, eventbutton, eventtime):
        """
        on right click on systry icon
        :param icon:
        :param eventbutton:
        :param eventtime:
        """
                
        self.showPopupMenu(eventbutton, eventtime)
        
    def onAskForItems(self, widget):
        """
        event handlet
        just consume the useless widget param
        :param widget:
        """
        
        self.askForItems()    

    def showPopupMenu(self, eventbutton, eventtime):
        """
        show (and also create) systry menu
        assemble menu items
        :param eventbutton:
        :param eventtime:
        """
        
        if not self.items:
            self.askForItems()
            
        reqreload = gtk.MenuItem(u'\u21BB', False)
        reqreload.show()
        reqreload.connect('activate', self.onAskForItems)

        about = gtk.MenuItem(u'\u00A9', False)
        about.show()
        about.connect('activate', self.showAbout)
        
        #quit = gtk.MenuItem("Quit", False)
        #quit.show()
        #quit.connect('activate', gtk.main_quit)

        menu =  gtk.Menu()
        for plugin_name in self.items:
            menu = self.createMenu(self.items[plugin_name], plugin_name, menu)

        menu.append(reqreload)
        menu.append(about)
        #menu.append(quit)
        
        menu.popup(None, None, gtk.status_icon_position_menu, eventbutton, eventtime, self.systray)

    def showAbout(self, widget):
        """
        about dialog
        :param widget:
        """
                        
        about = gtk.AboutDialog()        
        about.set_destroy_with_parent(True)
        about.set_icon_name ("ikona")        
        about.set_name(CONST.APP_NAME)
        about.set_version(CONST.VERSION)
        about.set_copyright(CONST.COPYRIGHT)
        about.set_comments((CONST.DESCRIPTION))
        about.set_authors(CONST.AUTHORS)
        about.run()
        about.destroy()
        
        
    def createMenu(self, items, cmdpath, menu = None):
        """
        create main menu and recursively submenus
        :param items: subtree with remaining items to create
        :param cmdpath: items full string
        :param menu: already created
        """
                
        if not menu:
            menu =  gtk.Menu()
            
        addlater = []
        for item in items.keys():
            
            later = False 
            for mi in menu:
                #if not isinstance(items[item], dict):
                #    continue
                
                if mi.get_label() == item:
                    addlater.append(item)
                    later = True
                    
                    submi=mi.get_submenu()
                    self.createMenu(items[item], cmdpath + CONST.DELIMITER + item, submi)
                    break
                
            if later:
                continue

            menuitem = gtk.MenuItem(item, False)
            menuitem.show()                    
            
            if isinstance(items[item], dict):
                menuitem.set_submenu(self.createMenu(items[item], cmdpath + CONST.DELIMITER + item ))
            else:
                menuitem.connect('activate', self.menuHandler, cmdpath + CONST.DELIMITER + item)
          
            menu.append(menuitem)
                      
        return menu

    def menuHandler(self, widget, data = None):   
        """
        handle data when menu item used
        :param widget: 
        :param data: full item string
        """
                
        target = data.split(CONST.DELIMITER)[0]
        cmdstring = CONST.DELIMITER.join(data.split(CONST.DELIMITER)[1:])
        
        logger.logDebug("Sending cmd for %s: '%s'" % (target, cmdstring) )
        self.sendCommands([cmdstring], target)

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