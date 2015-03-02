#!/usr/bin/python
"""
  Basic class for communication to Parrot Bebop
  usage:
       ./bebop.py <task> [<metalog> [<F>]]
"""
import sys
import socket
import datetime
import struct
from navdata import *
from commands import *

# this will be in new separate repository as common library fo robotika Python-powered robots
from apyros.metalog import MetaLog, disableAsserts
from apyros.manual import myKbhit, ManualControlException


# hits from https://github.com/ARDroneSDK3/ARSDKBuildUtils/issues/5

HOST = "192.168.42.1"
DISCOVERY_PORT = 44444

NAVDATA_PORT = 43210 # d2c_port
COMMAND_PORT = 54321 # c2d_port

class Bebop:
    def __init__( self, metalog=None ):
        if metalog is None:
            self._discovery()
            metalog = MetaLog()
        self.navdata = metalog.createLoggedSocket( "navdata", headerFormat="<BBBI" )
        self.navdata.bind( ('',NAVDATA_PORT) )
        self.command = metalog.createLoggedSocket( "cmd", headerFormat="<BBBI" )
        self.console = metalog.createLoggedInput( "console", myKbhit ).get
        self.metalog = metalog
        self.buf = ""
        self.videoCbk = None
        self.battery = None
        self.flyingState = None
        self.flatTrimCompleted = False
        self.manualControl = False
        self.time = None
        self.altitude = None
        self.config()
        
    def _discovery( self ):
        "start communication with the robot"
        filename = "tmp.bin" # TODO combination outDir + date/time
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP
        s.connect( (HOST, DISCOVERY_PORT) )
        s.send( '{"controller_type":"computer", "controller_name":"katarina", "d2c_port":"43210"}' )
        f = open( filename, "wb" )
        while True:
            data = s.recv(10240)
            if len(data) > 0:
                print len(data)
                f.write(data)
                f.flush()
                break
        f.close()
        s.close()

    def _update( self, cmd ):
        "internal send command and return navdata"
        
        if not self.manualControl:
            self.manualControl = self.console()
            if self.manualControl:
                # raise exception only once
                raise ManualControlException()

        while len(self.buf) == 0:
            data = self.navdata.recv(4094)
            self.buf += data
        if cmd is not None:
            self.command.sendto( cmd, (HOST, COMMAND_PORT) )
        self.command.separator( "\xFF" )
        data, self.buf = cutPacket( self.buf )
        return data

    def _parseData( self, data ):
        try:
            parseData( data, robot=self, verbose=False )
        except AssertionError, e:
            print "AssertionError", e


    def update( self, cmd ):
        "send command and return navdata"
        if cmd is None:
            data = self._update( None )
        else:
            data = self._update( packData(cmd) )
        while True:
            if ackRequired(data):
                self._parseData( data )
                data = self._update( createAckPacket(data) )
            elif pongRequired(data):
                self._parseData( data ) # update self.time
                data = self._update( createPongPacket(data) )
            elif videoAckRequired(data):
                if self.videoCbk:
                    self.videoCbk( data )
                data = self._update( createVideoAckPacket(data) )
            else:
                break
        self._parseData( data )
        return data

    def config( self ):
        # initial cfg
        dt = self.metalog.now()
        self.update( cmd=setDateCmd( date=dt.date() ) )
        self.update( cmd=setTimeCmd( time=dt.time() ) )
        self.update( videoAutorecordingCmd( enabled=True ) )


    def takeoff( self ):
        print "Taking off ...",
        self.update( cmd=takeoffCmd() )
        prevState = None
        for i in xrange(100):
            print i,
            self.update( cmd=None )
            if self.flyingState != 1 and prevState == 1:
                break
            prevState = self.flyingState
        print "FLYING"
        
    def land( self ):
        print "Landing ...",
        self.update( cmd=landCmd() )
        for i in xrange(100):
            print i,
            self.update( cmd=None )
            if self.flyingState == 0: # landed
                break
        print "LANDED"
        self.update( videoRecording( on=False ) ) # autorecording does not stop it (???)
        for i in xrange(30):
            print i,
            self.update( cmd=None )
        print

    def emergency( self ):
        self.update( cmd=emergencyCmd() )

    def trim( self ):
        print "Trim:", 
        self.flatTrimCompleted = False
        for i in xrange(10):
            print i,
            self.update( cmd=None )
        print
        self.update( cmd=trimCmd() )
        for i in xrange(10):
            print i,
            self.update( cmd=None )
            if self.flatTrimCompleted:
                break
   
    def takePicture( self ):
        self.update( cmd=takePictureCmd() )

    def videoEnable( self ):
        "enable video stream?"
        # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
        # ARCOMMANDS_ID_ARDRONE3_CLASS_MEDIASTREAMING = 21,
        # ARCOMMANDS_ID_ARDRONE3_MEDIASTREAMING_CMD_VIDEOENABLE = 0,        
        self.update( cmd=struct.pack("BBHB", 1, 21, 0, 1) )

    def moveCamera( self, tilt, pan ):
        "Tilt/Pan camera consign for the drone (in degrees)"
        # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
        # ARCOMMANDS_ID_ARDRONE3_CLASS_CAMERA = 1,
        # ARCOMMANDS_ID_ARDRONE3_CAMERA_CMD_ORIENTATION = 0,
        self.update( cmd=struct.pack("BBHbb", 1, 1, 0, tilt, pan) )

    def resetHome( self ):
        # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1
        # ARCOMMANDS_ID_ARDRONE3_CLASS_GPSSETTINGS = 23
        # ARCOMMANDS_ID_ARDRONE3_GPSSETTINGS_CMD_RESETHOME = 1
        self.update( cmd=struct.pack("BBH", 1, 23, 1) )


    def wait( self, duration ):
        print "Wait", duration
        assert self.time is not None
        startTime = self.time
        while self.time-startTime < duration:
            self.update()

    def flyToAltitude( self, altitude, timeout=3.0 ):
        print "Fly to altitude", altitude, "from", self.altitude
        speed = 20 # 20%
        assert self.time is not None
        assert self.altitude is not None
        startTime = self.time
        if self.altitude > altitude:
            while self.altitude > altitude and self.time-startTime < timeout:
                self.update( movePCMDCmd( True, 0, 0, 0, -speed ) )
        else:
            while self.altitude < altitude and self.time-startTime < timeout:
                self.update( movePCMDCmd( True, 0, 0, 0, speed ) )
        self.update( movePCMDCmd( True, 0, 0, 0, 0 ) )



###############################################################################################

def testCamera( robot ):
    for i in xrange(10):
        print -i,
        robot.update( cmd=None )
    robot.resetHome()
    robot.videoEnable()
    for i in xrange(100):
        print i,
        robot.update( cmd=None )
        robot.moveCamera( tilt=i, pan=i ) # up & right


def testEmergency( robot ):
    "test of reported state change"
    robot.takeoff()
    robot.emergency()
    for i in xrange(10):
        print i,
        robot.update( cmd=None )


def testTakeoff( robot ):
    robot.videoEnable()
    robot.takeoff()
    for i in xrange(100):
        print i,
        robot.update( cmd=None )
    robot.land()
    for i in xrange(100):
        print i,
        robot.update( cmd=None )
    print


def testManualControlException( robot ):
    robot.videoEnable()
    try:
        robot.trim()
        robot.takeoff()
        robot.land()
    except ManualControlException, e:
        print
        print "ManualControlException"
        if robot.flyingState is None or robot.flyingState == 1: # taking off
            # unfortunately it is not possible to land during takeoff for ARDrone3 :(
            robot.emergency()
        robot.land()


def testFlying( robot ):
    robot.videoEnable()
    try:
        robot.trim()
        robot.takeoff()
        robot.flyToAltitude( 2.0 )
        robot.wait( 2.0 )
        robot.flyToAltitude( 1.0 )
        robot.land()
    except ManualControlException, e:
        print
        print "ManualControlException"
        if robot.flyingState is None or robot.flyingState == 1: # taking off
            # unfortunately it is not possible to land during takeoff for ARDrone3 :(
            robot.emergency()
        robot.land()


def testTakePicture( robot ):
    print "TEST take picture"
    robot.videoEnable()
    for i in xrange(10):
        print i,
        robot.update( cmd=None )
    robot.takePicture()
    for i in xrange(10):
        print i,
        robot.update( cmd=None )


def videoCallback( data ):
    print "Video", len(data)

def testVideoProcessing( robot ):
    print "TEST video"
    robot.videoCbk = videoCallback
    robot.videoEnable()
    for i in xrange(10):
        print i,
        robot.update( cmd=None )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    metalog=None
    if len(sys.argv) > 2:
        metalog = MetaLog( filename=sys.argv[2] )
    if len(sys.argv) > 3 and sys.argv[3] == 'F':
        disableAsserts()

    robot = Bebop( metalog=metalog )
#    testCamera( robot )
#    testEmergency( robot )
#    testTakeoff( robot )
#    testManualControlException( robot )
    testTakePicture( robot )
#    testFlying( robot )
#    testVideoProcessing( robot )
    print "Battery:", robot.battery

# vim: expandtab sw=4 ts=4 

