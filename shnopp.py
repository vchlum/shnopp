#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys
sys.dont_write_bytecode = True

import os
import stat
import time
import threading
import pkgutil


os.chdir(os.path.dirname(os.path.abspath(__file__)))

from config import CFG
from config import CONST
from config import EVENT

from misc import *


"""
main init system
"""
try:
    # create and set working dirs
    if not os.path.exists(CFG.DIR_RUN):
        os.makedirs(CFG.DIR_RUN)
    os.chmod(CFG.DIR_RUN, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    if not os.path.exists(CFG.DIR_VAR):
        os.makedirs(CFG.DIR_VAR)
    os.chmod(CFG.DIR_VAR, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

except Exception as err:
    print "dir error: %s" % str(err)
    sys.exit(CONST.RET_ERROR)


def print_usage():
    """
    print usage
    """
    
    print "usage: %s start|stop|restart [-d|--debug]" % sys.argv[0]

class MainDaemon(daemon.Daemon):
    """
    main daemon class - this is the core - child of deaemon
    """

    nodes = {} # nodes in neighbourhood
    plugins = {} # loaded plugins
    passthrough_clients = []


    def handleData(self, data_dict, addr):
        """
        handleData - main data handler
        :param data_dict: data in python dictionary, preHandler guarantees data in dict
        :param addr: addr from
        """

        if isinstance(addr, tuple):
            nodename = str(addr[0])
        else:
            nodename = str(addr)
        
        if nodename not in self.nodes.keys():
            self.nodes[nodename] = {}
            self.nodes[nodename]["addr"] = addr
            logger.logInfo("New node '%s' discovered" % nodename)
        """    
        if not from sockfile - pass to sock file
        """
        if addr != '':
            for client in self.passthrough_clients:

                if str(client.addr) == "":
                    client.sendDictAsJSON(data_dict)
        
        """
        if from sockfile - broadcast
        """
        if False and addr == '': 
            conn = communicator.Connector()
            conn.send=self.broadcastData
            conn.sendDictAsJSON(data_dict)
        
            """
            The data has been broadcasted anyway, end this finction...
            """
            if CFG.SOCKET_TCP_ENABLED or CFG.SOCKET_UDP_ENABLED:
                return communicator.MESSAGE_OK
                        
        plugins_with_receiver = [key for key in self.plugins.keys() if "receiver" in self.plugins[key].keys()]

        status = "noreceiver"
        
        for plugin_name in plugins_with_receiver:
            
            threading.Thread(target=self.plugins[plugin_name]["receiver"], args=(data_dict,)).start()

            logger.logDebug("Recieved data passed to %s plugin." % plugin_name)

            status = communicator.MESSAGE_OK
   
        return status
    
    def pluginSender(self, data):
        """
        pluginSender - sender used by plugins
        :param data: 
        """
        
        if CFG.SOCKET_UDP_ENABLED:
            self.broadcastData(data)
        
        for client in self.passthrough_clients:
            client.sendData(data)

    def sendDataTo(self, addr, data):
        """
        sendDataTo - TODO: create client and send
        """
        
        pass

    def sendDataToAll(self, data):
        """
        sendDataToAll - send TCP data to all nodes
        :param data: 
        """
        
        logger.logDebug("Sending to all data: '%s'" % (", ".join(self.nodes.keys()), str(data)))

        for addr in self.nodes.keys():
            threading.Thread(target=self.sendDataTo, args=(addr, data)).start()

    def broadcastData(self, data):
        """
        broadcastData - UDP broadcaster
        :param data: 
        """
        
        logger.logDebug("Broadcasting data: '%s'" % str(data))

        broadcast = communicator.SocketClient((communicator.BROADCAST_HOST, CFG.SOCKET_UDP_PORT), communicator.SOCKET_UDP)
        if broadcast.initClient() != CONST.RET_OK:
            logger.logError("Broadcasting data: '%s' failed" % str(data))
        broadcast.keepAlive(False) #default
        broadcast.useReplying(False) #default
        broadcast.sendData(data)
        broadcast.close()
            
    def startEventServer(self):
        """
        startEventServer - start enabled servers (tcp, udp, socket file)
        :param data: 
        """        

        if CFG.SOCKET_TCP_ENABLED:
            """
            Start TCP server
            """
            
            addr = (CFG.SOCKET_TCP_HOSTNAME, CFG.SOCKET_TCP_PORT)
            server_tcp = communicator.SocketServer(addr, communicator.SOCKET_TCP)
            server_tcp.keepAlive(True)
            server_tcp.useReplying(CFG.SOCKET_TCP_ENABLE_REPLY)
            server_tcp.setDataHandler(self.handleData)
            if server_tcp.startServer() == CONST.RET_OK:
                server_tcp.listenServer()
            else:
                logger.logError("Starting TCP server failed")

        if CFG.SOCKET_UDP_ENABLED:
            """
            Start UDP server
            """
            
            addr = (CFG.SOCKET_UDP_HOSTNAME, CFG.SOCKET_UDP_PORT)
            server_udp = communicator.SocketServer(addr, communicator.SOCKET_UDP)
            server_udp.keepAlive(False)
            server_udp.useReplying(CFG.SOCKET_UDP_ENABLE_REPLY)
            server_udp.setDataHandler(self.handleData)
            if server_udp.startServer() == CONST.RET_OK:
                server_udp.listenServer()
            else:
                logger.logError("Starting UDP server failed")            

        if CFG.SOCKET_UNIX_ENABLED:
            """
            Start socket file
            """
            
            addr = CFG.SOCKET_UNIX_FILE
            server_unixfile = communicator.SocketServer(addr, communicator.SOCKET_TCP)
            server_unixfile.keepAlive(True)
            server_unixfile.useReplying(CFG.SOCKET_UNIX_ENABLE_REPLY)
            server_unixfile.setDataHandler(self.handleData)
            if server_unixfile.startServer() == CONST.RET_OK:
                server_unixfile.listenServer()
                self.passthrough_clients = server_unixfile.clients
            else:
                logger.logError("Starting unixfile server failed")            

        """
        TODO: UDP Discovery
        """

    def loadPlugins(self):
        """
        load plugins from plugin folder as modules
        """
        
        import plugins

        def onerror(msg):
            logger.logError("Error importing plugin %s" % msg)
            
        for importer, plugin_name, ispkg in pkgutil.walk_packages(plugins.__path__, plugins.__name__ + ".",  onerror):
            parsed_plugin_name = plugin_name.split(".")

            if ispkg:
                continue
            
            if len(parsed_plugin_name) > 3:
                continue # no sub sub files
            
            if len(parsed_plugin_name) == 3 and parsed_plugin_name[1] != parsed_plugin_name[2]:
                continue # if in dir only same name

            """
            debug - disable plugins, list of plugin_name
            """
            #disabled = ["gui_web", "system"]
            disabled = ["gui"]
            if parsed_plugin_name[-1] in disabled:
                continue
            
            try:
                loader = importer.find_module(plugin_name)                
                plugin_module = loader.load_module(plugin_name)
                plugin_name = parsed_plugin_name[-1]

            except Exception as err:
                logger.logWarning("Plugin %s not loaded. %s" % (plugin_name, str(err)) )

            else:
                self.plugins[plugin_name] = {}
                self.plugins[plugin_name]["module"] = plugin_module
                self.plugins[plugin_name]["ready"] = False

                logger.logInfo("Plugin %s successfully loaded." % plugin_name )
    
    def initPlugins(self):
        """
        call init function of each plugin
        """
                
        for plugin_name in self.plugins.keys():
            plugin = self.plugins[plugin_name]
            
            try:
                plugin["instance"] = plugin["module"].Plugin(plugin_name)
                plugin["instance"].setSender(self.pluginSender)
                if plugin["instance"].receiverhandler:
                    plugin["receiver"] = plugin["instance"].receiverhandler
                plugin["ready"] = True
                
                logger.logInfo("Plugin %s ready" % plugin_name )

            except Exception as err:
                logger.logWarning("Init plugin %s error: %s" % (str(plugin_name), str(err)) )


    def run(self):
        """
        main run - loop
        """        
        
        self.loadPlugins()
        self.initPlugins()
        
        self.startEventServer()

        logger.logInfo("%s is running and ready" % CONST.APP_NAME)
        logger.logDebug("Receivers ready: %s" % str([ i for i in self.plugins.keys() if "receiver" in self.plugins[i].keys()]))

        while True:
            time.sleep(30)



if __name__ == "__main__":
    """
    deamon starter
    """
    
    debug = False

    if "--debug" in sys.argv or "-d" in sys.argv:
        debug = True

    if not debug:
        logger.closestdIO()
        logger.startLogFile(CONST.APP_SHORT_NAME, CFG.LOG_FORMAT, CFG.LOG_FILE)
        logger.redirectStdout()
        logger.redirectStderr()
        logger.logInfo("stdout and stderr redirected")
        
        
    daemon = MainDaemon(CFG.PID_FILE, debug)

    if len(sys.argv) > 1:
        if 'restart' in sys.argv:
            if daemon.stop() != CONST.RET_OK or daemon.start() != CONST.RET_OK:
                logger.logError("Restarting failed")

        elif 'stop' in sys.argv:
            if daemon.stop() > CONST.RET_OK:
                logger.logError("Stopping failed")

        elif 'start' in sys.argv:
            if daemon.start() > CONST.RET_OK:
                logger.logError("Starting failed")

        else:
            logger.logError("Unknown deamon command: %s" % " ".join(sys.argv))
            print_usage()
            sys.exit(CONST.RET_ERROR)

        sys.exit(CONST.RET_OK)

    else:
        print_usage()
        sys.exit(CONST.RET_ERROR)
