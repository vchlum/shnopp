#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import socket 
import threading
import os
import time

import json

from config import CONST
from config import EVENT
from config import CMD
from config import METHOD

from misc import logger
from __builtin__ import dict

SOCKET_TCP = socket.SOCK_STREAM
SOCKET_UDP = socket.SOCK_DGRAM

BROADCAST_HOST = "<broadcast>"

MESSAGE_OK = "ok"
MESSAGE_HANDLER_ERROR = "handler_failed"

EXIT_DATA = [None, [], {}, "", "exit", "e", "quit", "q", "error"]



############################################
### tools and helpers                    ###
############################################
############################################
############################################

#########################
### convert unicode dict to utf-8 dict
# thx to: http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python
def byteify(inputstring):
    if isinstance(inputstring, dict):
        return {byteify(key):byteify(value) for key,value in inputstring.iteritems()}
    elif isinstance(inputstring, list):
        return [byteify(element) for element in inputstring]
    elif isinstance(inputstring, unicode):
        return inputstring.encode('utf-8')
    else:
        return inputstring



####################################################################
####################################################################
####################################################################
### classes for communication                                    ###
####################################################################
####################################################################
####################################################################



############################################
### conector                             ###
############################################
### add conversion to/from JRPC ############
############################################

class Connector(object):

    #########################
    ###
    #
    def send(self, data):
        logger.logWarning("Using dump send! Nothing happend.")
        return

    #########################
    ###
    #
    def sendData(self, data):
        return self.send(data)
    
    #########################
    ###
    #
    def sendDictAsJSON(self, dict_data):
        try:
            data = json.dumps(dict_data, encoding="utf-8")
        except Exception as err:
            logger.logError("Dump data to JSON failed: %s" % str(err))
            return CONST.RET_ERROR

        return self.sendData(data)
    
    #########################
    ###
    #
    def sendEvents(self, data, target = None):
        if not type(data) == list:
            data = [data]

        return self.sendJRPCRequest(METHOD.EVENT, {"target": target, "events": data})
    
    #########################
    ###
    #
    def sendCommands(self, data, target = None):
        if not type(data) == list:
            data = [data]

        return self.sendJRPCRequest(METHOD.CMD, {"target": target, "cmds": data})
        
    #########################
    ###
    #    
    def sendJRPCRequest(self, method, params, jrpc_id = None):
        dict_data = {"jsonrpc":"2.0", "method":method, "params": params}
        if jrpc_id:
            dict_data["id"] = jrpc_id
            
        return self.sendDictAsJSON(dict_data)

    #########################
    ###
    #        
    def getJRPCErrorObject(self, code, message, data = None):
        if data:
            return {"code": code, "message": message, "data": data}
        else:
            return {"code": code, "message": message}
    
    #########################
    ###
    #    
    def sendJRPCResponse(self, result, jrpc_id = None, error = None):
        dict_data = {}
        dict_data["result"] = result
        if jrpc_id:
            dict_data["id"] = jrpc_id        
        if error:
            dict_data["error"] = error
        dict_data["jsonrpc"] = "2.0"

        return self.sendDictAsJSON(dict_data)    
    
    #########################
    ###
    #
    def dataPreHandler(self, data, *args):
        data_dict = {}

        try:
            data_dict = json.loads(data)
            data_dict = byteify(data_dict)
        except Exception as err:
            data_dict = {}
            logger.logWarning("Data not in JSON: %s" % (str(err)))

        return (data_dict,) + args



############################################
### socket general corpus                ###
############################################
############################################
############################################

class Socket(object):

    #########################
    ###
    #
    def __init__(self, addr=("",None), protocol = SOCKET_TCP):
        self.addr = addr
        self.protocol = protocol
        self.sock = None

        if isinstance(self.addr, tuple):
            self.af = socket.AF_INET
        else:
            self.af = socket.AF_UNIX

        self.datahandler = self.dataHandler
        self.replying = False
        self.keepalive = False

    #########################
    ###
    #
    def __del__(self):
        self.close()

    #########################
    ###
    #
    def dataHandler(self, recv_data, addr):
        logger.logWarning("Data from '%s' not handled. Received data: '%s'" % (str(addr), str(recv_data).strip()))
        return MESSAGE_OK

    #########################
    ###
    #
    def setDataHandler(self, handler = dataHandler):
        self.datahandler = handler

    #########################
    ###
    #
    def useReplying(self, replying):
        self.replying = replying

    #########################
    ###
    #
    def keepAlive(self, keepalive = True):
        self.keepalive = keepalive

    #########################
    ###
    #
    def keepAliveThread(self, starter, immortal):
        attempcounter = 0
        while True:

            try:
                immortal()
            except Exception as err:
                logger.logError("Always alive process error: %s" % str(err))

            if self.keepalive:
                attempcounter += 1

                if attempcounter % 3 == 0:
                    waittime = attempcounter
                else:
                    waittime = 1

                time.sleep(min(180, waittime))

                if starter() != CONST.RET_OK:
                    logger.logWarning("Resuscitation function failed")
                continue

            break

    #########################
    ###
    #
    def close(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except:
            pass

        self.sock = None



############################################
### socket server                        ###
############################################
############################################
############################################
#
### use example:
# server = SocketServer(("localhost", 1234), SOCKET_TCP)
# server.startServer()
# server.keepAlive(True)
# server.useReplying(True)
# server.setDataHandler(myawesomehandlerreturningreply(data, from))
# server.listenServer()
#

class SocketServer(Socket):
    clients = []
    #########################
    ###
    #
    def __init__(self, addr=("",None), protocol = SOCKET_TCP):
        super(SocketServer, self).__init__(addr, protocol)

    #########################
    ###
    #
    def startServer(self):
        self.close()

        try:
            self.sock = socket.socket(self.af, self.protocol)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            self.sock.settimeout(None)
            self.sock.setblocking(1)
            self.sock.bind(self.addr)

            if self.protocol == SOCKET_TCP:
                self.sock.listen(5)

        except socket.error as err:
            logger.logError("Starting socket server on '" + str(self.addr)+ "' failed. Error Code: " + str(err[0]) + ' Message: ' + err[1])
            self.sock = None 
            return CONST.RET_ERROR
        return CONST.RET_OK

    #########################
    ###
    #
    def listenServer(self):
        logger.logDebug("Starting listener on '%s'" % str(self.addr))
        
        if self.protocol == SOCKET_TCP:
            listenerthread = self.listenTCPThread

        if self.protocol == SOCKET_UDP:
            listenerthread = self.listenUDPThread

        if self.keepalive:
            t_target = self.keepAliveThread
            t_args = (self.startServer, listenerthread)
        else:
            t_target = listenerthread
            t_args = ()

        t = threading.Thread(target = t_target, args = t_args)
        t.setDaemon(True)
        t.start()

    #########################
    ###
    #
    def listenTCPThread(self):
        logger.logInfo("TCP listener started on '%s'" % str(self.addr))

        while True:
            try:
                (client_sock, client_addr) = self.sock.accept()
            except socket.error as err:
                logger.logError("Failed to accept TCP connection. Error Code: " + str(err[0]) + ' Message: ' + err[1])
                break

            logger.logDebug("Connection with '%s' accepted." % str(client_addr))
            threading.Thread(target=self.startComunication, args=(client_addr, client_sock)).start()

        logger.logInfo("TCP listener on '%s' ended" % str(self.addr))

    #########################
    ###
    #
    def listenUDPThread(self):
        while True:
            if not self.sock:
                break
            
            logger.logInfo("UDP listener started on '%s'" % str(self.addr))

            self.startComunication(self.addr, self.sock)

            logger.logInfo("UDP listener on '%s' ended" % str(self.addr))

    #########################
    ###
    #
    def startComunication(self, client_addr, client_sock):
        client = SocketClient(client_addr, self.protocol)
        self.clients.append(client) 
        client.setDataHandler(self.datahandler)
        client.useReplying(self.replying)
        client.keepAlive(False)
        client.setConnectedSocket(client_sock)
        client.responseLoop()
        self.clients.remove(client)
        client.close()

    #########################
    ###
    #
    def close(self):
        super(SocketServer, self).close()

        try:
            if not isinstance(self.addr, tuple):
                os.remove(self.addr)
        except:
            pass



############################################
### socket client                        ###
############################################
############################################
############################################
#
### use example:
# client = SocketClient(("localhost", 1234), SOCKET_TCP)
# client.initClient()
# client.send("awesome message")
# client.keepAlive(True)
# client.useReplying(True)
# client.setDataHandler(myawesomehandler(data, from))
# client.startReceiving()
#
# or
#
# client = SocketClient((BROADCAST_HOST, 1234), SOCKET_UDP)
# client.initClient()
# client.keepAlive(False) #default
# client.useReplying(False) #default
# client.send("awesome broadcast message")
#

class SocketClient(Socket, Connector):

    #########################
    ###
    #
    def __init__(self, addr=("",None), protocol = SOCKET_TCP):
        super(SocketClient, self).__init__(addr, protocol)

    #########################
    ###
    #
    def initClient(self):
        self.close()

        if isinstance(self.addr, tuple) and self.addr[0] == BROADCAST_HOST:
            addtional_option =  socket.SO_BROADCAST
        else:
            addtional_option =  socket.SO_REUSEADDR

        try:
            self.sock = socket.socket(self.af, self.protocol)
            self.sock.setsockopt(socket.SOL_SOCKET, addtional_option, 1)
            self.sock.settimeout(None)
            self.sock.setblocking(1)

            if self.protocol == SOCKET_TCP:
                self.sock.connect(self.addr)

        except socket.error as err:
            logger.logError("Initilizing socket client failed. Error Code: " + str(err[0]) + ' Message: ' + err[1])
            self.sock = None 
            return CONST.RET_ERROR

        return CONST.RET_OK

    #########################
    ###
    #
    def setConnectedSocket(self, sock):
        self.sock = sock

    #########################
    ###
    #
    def recv(self):
        (recv_data, addr) = (None, None)

        if not self.sock:
            logger.logError("Cant't receive data. Socket not ready")
            return (None, None)
        
        try:
            if self.protocol == SOCKET_TCP:
                recv_data = self.sock.recv(2048)
                addr = self.addr

            if self.protocol == SOCKET_UDP:
                recv_data, addr = self.sock.recvfrom(2048)
                
        except socket.error as err:
            logger.logError("Receiving data failed. Error Code: " + str(err[0]) + ' Message: ' + err[1])
            return (None, None)

        #logger.logDebug("Data: '%s' received from: '%s'" % (str(recv_data).strip(), str(addr)))
        return (recv_data, addr)

    #########################
    ###
    #
    def send(self, data, addr = None):
        if not addr:
            addr = self.addr
            
        if not self.sock:
            self.initClient() # conection error? try repair...

        if not self.sock:
            logger.logError("Cant't send data '%s' to '%s'. Socket not ready" % (str(data).strip(), str(addr)))
            return CONST.RET_IO_ERROR
            
        try:
            if self.protocol == SOCKET_TCP:
                self.sock.send(data)

            if self.protocol == SOCKET_UDP:
                self.sock.sendto(data, addr)

        except socket.error as err:
            logger.logError("Sending data failed. Error Code: " + str(err[0]) + ' Message: ' + err[1])
            return CONST.RET_IO_ERROR

        #logger.logDebug("Data: '%s' sent to '%s'" % (str(data).strip(), str(addr)))
        return CONST.RET_OK

    #########################
    ###
    #
    def responseLoop(self):
        logger.logDebug("Waiting for message main loop")

        while True:
            logger.logDebug("Waiting for message...")
            (recv_data, addr) = self.recv()

            if recv_data in EXIT_DATA:
                break

            (recv_data, addr) = self.dataPreHandler(recv_data, addr)

            try:
                reply_data = self.datahandler(recv_data, addr)
            except Exception as err:
                logger.logError("Handling data error: %s" % str(err))
                reply_data = MESSAGE_HANDLER_ERROR

            if not self.replying:
                continue

            self.send(reply_data, addr)

            if reply_data in EXIT_DATA:
                break

    #########################
    ###
    #
    def startReceiving(self):
        if self.keepalive:
            t_target = self.keepAliveThread
            t_args = (self.initClient, self.responseLoop)
        else:
            t_target = self.responseLoop
            t_args = ()

        t = threading.Thread(target = t_target, args = t_args)
        t.setDaemon(True)
        t.start()
