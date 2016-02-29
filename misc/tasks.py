#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import Queue
import threading

from misc import logger


####################################################################
####################################################################
####################################################################
### queue sequent run task                                       ###
####################################################################
####################################################################
####################################################################



############################################
### tasks class                          ###
############################################
############################################
############################################

class Tasks(object):

    #########################
    ###
    #
    def __init__(self):
        self.handler = None
        threading.Thread(target=self.taskHandlerThread).start()

    #########################
    ###
    #
    def setTaskHandler(self, handler):
        self.handler = handler

    #########################
    ###
    #
    def putTask(self, task):
        self.tasks.put(task)

    #########################
    ###
    #
    def taskHandlerThread(self):
        logger.logDebug("Task thread started")

        self.tasks = Queue.Queue()
        while True:
            try:
                task = self.tasks.get()

                if self.handler:
                    try:
                        self.handler(task)
                    except Exception as err:
                        logger.logDebug("Task error: %s" % str(err))

                self.tasks.task_done()
            except:
                pass