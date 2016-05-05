#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys
import os
import time
import atexit
from signal import SIGTERM

from misc import logger
from config import CONST



class Daemon(object):
    """
    deamon class - inspired by:
    http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
    """

    def __init__(self, pidfile, debug):
        """
        deamon init function
        :param pidfile: used pidfile
        :param debug: True/False - affects forking
        """
        self.pidfile = pidfile
        self.debug = debug

    def daemonize(self):
        """
        daemonize process
        """
        
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            logger.logError("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            return CONST.RET_ERROR

        logger.logDebug("fork #1 finished")

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            logger.logError("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            return CONST.RET_ERROR

        logger.logDebug("fork #2 finished")

        try: # redirect standard file descriptors if not yet
            logger.closestdIO()
        except:
            pass

        # write pidfile
        atexit.register(self.delPID)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)

        logger.logInfo("Sucessfully daemonized with pid: %s" % pid)

        return CONST.RET_OK

    def delPID(self):
        """
        delete pidfile
        """
        
        try:
            os.remove(self.pidfile)
        except:
            logger.logError("Remove pidfile %s failed" % self.pidfile)

    def status(self):
        """
        check status
        """
        
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            return None

        try:
            # check if there exists a process with a given pid
            os.kill(pid, 0)
        except:
            self.delPID()
            return None

        return pid
        
    def start(self):
        """
        start main process
        if not debug - daemonize
        """
        logger.logInfo("Starting...")

        pid = self.status()

        if pid:
            logger.logError("Daemon already running with pid %s" % self.pidfile)
            return CONST.RET_ERROR

        # Start the daemon
        if not self.debug:
            logger.logDebug("Demonizing...")
            if self.daemonize() > CONST.RET_OK:
                return CONST.RET_ERROR

        logger.logInfo("Running")

        try:
            self.run()        
            logger.logDebug("Main loop finished")
        except Exception as err:
            logger.logError("Main loop error: %s" % str(err))
            
            return CONST.RET_ERROR

        return CONST.RET_OK

    def stop(self):
        """
        stop process
        """
        
        logger.logInfo("Stoping...")
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            logger.logInfo("Pidfile %s does not exist. Daemon not running." % self.pidfile)
            # no pidfile - no error
            return CONST.RET_OK

        #Try killing the daemon process
        try:
            logger.logDebug("Trying to kill pid %s" % pid)
            while True:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    self.delPID()
            else:
                logger.logError(str(err))
                return CONST.RET_ERROR

        logger.logInfo("Stopped")
        return CONST.RET_OK

    def restart(self):
        """
        restart process - stop and start again
        """
        logger.logInfo("Restarting...")
        if self.stop() == CONST.RET_OK:
            return self.start()

        return CONST.RET_ERROR

    def run(self):
        """
        default main loop - overwrite this
        """
        while True:
            time.sleep(30)
