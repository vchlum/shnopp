#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import Queue
import threading

from misc import logger



class Tasks(object):
    """
    tasker - queue sequent run task
    """

    def __init__(self):
        """
        init tasker, start main thread
        """
        
        self.handler = None
        threading.Thread(target=self.taskThread).start()

    def setTaskHandler(self, handler):
        """
        set tasks handler
        :param handler: every task is passed to this function
        """
        
        self.handler = handler

    def putTask(self, task):
        """
        enqueue new task
        :param task: task for task handler
        """
        
        self.tasks.put(task)

    def taskThread(self):
        """
        tasker main thread - loop 
        """
        
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