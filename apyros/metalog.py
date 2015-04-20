#!/usr/bin/python
"""
  MetaLog - binding of multiple log files
"""
# MetaLog serves three scenarios:
# 1) logging of several different sensor sources and effector commands
# 2) exact replay of the run (like from BlackBox)
# 3) fake replay when effectors commands are not asserted
# Note, that 3rd case can be split into two when at least send/receive
# structure is kept or even that is ignored.

import os
import datetime
import sys

from logio import ReplayLog, LoggedSocket
from sourcelogger import SourceLogger

global g_checkAssert
g_checkAssert = True # use command 'F' to disable it


def disableAsserts():
    global g_checkAssert
    g_checkAssert = False

class MetaLog:
    def __init__( self, filename=None ):
        if filename is None:
            self.replay = False
            if not os.path.exists("logs"):
                os.mkdir("logs")
            self.filename = datetime.datetime.now().strftime("logs/meta_%y%m%d_%H%M%S.log")
            sys.stderr.write( "METALOG: %s\n" % self.filename )
            self.f = open( self.filename, "w" )
            self.f.write( str(sys.argv)+"\n" )
            self.f.flush()
        else:
            self.replay = True
            self.filename = filename
            self.f = open( self.filename )

    def areAssertsEnabled( self ):
        global g_checkAssert
        return g_checkAssert

    def getLog( self, prefix ):
        if not self.replay:
            filename = "logs/" + prefix + datetime.datetime.now().strftime("_%y%m%d_%H%M%S.log") # bin? txt? log??
            self.f.write( prefix + ": " + filename + "\n")
            self.f.flush()
            return filename

        for line in self.f:
            print "LINE", line.strip()
            if line.startswith( prefix ):
                ret = line.split()[1].strip()
                assert ret.startswith("logs/")
                return os.path.dirname( self.filename ) + os.sep + ret[4:]
        return None # not found


    def createLoggedSocket( self, prefix, headerFormat ):
        if self.replay:
            return ReplayLog( self.getLog( prefix ), headerFormat=headerFormat, checkAssert=g_checkAssert )
        else:
            filename = "logs/" + prefix + datetime.datetime.now().strftime("_%y%m%d_%H%M%S.bin") # bin? txt? log??
            self.f.write( prefix + ": " + filename + "\n")
            self.f.flush()
            return LoggedSocket( filename )

    def createLoggedInput( self, prefix, function ):
        if self.replay:
            return SourceLogger( None, self.getLog( prefix ) )
        else:
            filename = "logs/" + prefix + datetime.datetime.now().strftime("_%y%m%d_%H%M%S.txt") # bin? txt? log??
            self.f.write( prefix + ": " + filename + "\n")
            self.f.flush()
            return SourceLogger( function, filename )

    def now( self ):
        "get logged datetime"
        if self. replay:
            dt = None
            for line in self.f:
                print "LINE", line.strip()
                if line.startswith( "now:" ):
                    dt = eval(line[4:].strip())
                    break
        else:
            dt = datetime.datetime.now() 
            self.f.write( "now: " + repr(dt) + "\n")
            self.f.flush()
        return dt

# vim: expandtab sw=4 ts=4 

