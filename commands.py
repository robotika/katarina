"""
  Encode Parrot Bebop commands
  (possible usage also as parsing command log files)
  usage:
      ./commands.py <cmd log file>
"""
import time
import struct
from threading import Thread,Event,Lock
from collections import defaultdict

def takeoffCmd():
    # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
    # ARCOMMANDS_ID_ARDRONE3_CLASS_PILOTING = 0,
    # ARCOMMANDS_ID_ARDRONE3_PILOTING_CMD_TAKEOFF = 1,
    return struct.pack("BBH", 1, 0, 1)
      
def landCmd():
    # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
    # ARCOMMANDS_ID_ARDRONE3_CLASS_PILOTING = 0,
    # ARCOMMANDS_ID_ARDRONE3_PILOTING_CMD_LANDING = 3,
    return struct.pack("BBH", 1, 0, 3)

def emergencyCmd():
    # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
    # ARCOMMANDS_ID_ARDRONE3_CLASS_PILOTING = 0,
    # ARCOMMANDS_ID_ARDRONE3_PILOTING_CMD_EMERGENCY = 4,
    return struct.pack("BBH", 1, 0, 4)

def trimCmd():
    # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
    # ARCOMMANDS_ID_ARDRONE3_CLASS_PILOTING = 0,
    # ARCOMMANDS_ID_ARDRONE3_PILOTING_CMD_FLATTRIM = 0,
    return struct.pack("BBH", 1, 0, 0)


def movePCMDCmd( active, roll, pitch, yaw, gaz ):
    # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
    # ARCOMMANDS_ID_ARDRONE3_CLASS_PILOTING = 0,
    # ARCOMMANDS_ID_ARDRONE3_PILOTING_CMD_PCMD = 2,
    psi = 0.0 # Magnetic north heading of the controlling device (deg) [-180;180]
    flag = 0
    if active:
        flag = 1
    return struct.pack("<BBHBbbbbf", 1, 0, 2, flag, roll, pitch, yaw, gaz, psi )


def videoAutorecordingCmd( enabled=True ):
    # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
    # ARCOMMANDS_ID_ARDRONE3_CLASS_PICTURESETTINGS = 19,    
    # ARCOMMANDS_ID_ARDRONE3_PICTURESETTINGS_CMD_VIDEOAUTORECORDSELECTION = 5,
    massStorageId = 0 # internal ??
    if enabled:
        return struct.pack("BBHBB", 1, 19, 5, 1, massStorageId)
    else:
        return struct.pack("BBHBB", 1, 19, 5, 0, massStorageId)


def takePictureCmd():
    # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
    # ARCOMMANDS_ID_ARDRONE3_CLASS_MEDIARECORD = 7,
    # ARCOMMANDS_ID_ARDRONE3_MEDIARECORD_CMD_PICTURE = 0,
    massStorageId = 0 # internal ??
    return struct.pack("BBHB", 1, 7, 0, massStorageId)


def videoRecordingCmd( on=True ):
    # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
    # ARCOMMANDS_ID_ARDRONE3_CLASS_MEDIARECORD = 7,
    # ARCOMMANDS_ID_ARDRONE3_MEDIARECORD_CMD_VIDEO = 1
    massStorageId = 0 # internal ??
    if on:
        return struct.pack("BBHIB", 1, 7, 1, 1, massStorageId)
    else:
        return struct.pack("BBHIB", 1, 7, 1, 0, massStorageId)


def setDateCmd( date ):
    # ARCOMMANDS_ID_PROJECT_COMMON = 0,
    # ARCOMMANDS_ID_COMMON_CLASS_COMMON = 4,
    # ARCOMMANDS_ID_COMMON_COMMON_CMD_CURRENTDATE = 1,
    # Date with ISO-8601 format
    return struct.pack("BBH", 0, 4, 1) + date.isoformat() + '\0'

def setTimeCmd( time ):    
    # ARCOMMANDS_ID_PROJECT_COMMON = 0,
    # ARCOMMANDS_ID_COMMON_CLASS_COMMON = 4,
    # ARCOMMANDS_ID_COMMON_COMMON_CMD_CURRENTTIME = 2,
    # Time with ISO-8601 format
    # note, that "time.isoformat()" did not work '19:39:22.887000' milisec??
    return struct.pack("BBH", 0, 4, 2) + time.strftime("T%H%M%S+0000") + '\0'


def setSpeedSettingsCmdList( maxVerticalSpeed, maxRotationSpeed, hullProtection, outdoor ):
    # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
    # ARCOMMANDS_ID_ARDRONE3_CLASS_SPEEDSETTINGS = 11,
    # ARCOMMANDS_ID_ARDRONE3_SPEEDSETTINGS_CMD_MAXVERTICALSPEED = 0,
    return [ struct.pack("BBHf", 1, 11, 0, maxVerticalSpeed), # Current max vertical speed in m/s
            struct.pack("BBHf", 1, 11, 1, maxRotationSpeed), # Current max rotation speed in degree/s
            struct.pack("BBHB", 1, 11, 2, hullProtection),
            struct.pack("BBHB", 1, 11, 3, outdoor) ]


def videoStreamingCmd( enable ):
    "enable video stream?"
    # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
    # ARCOMMANDS_ID_ARDRONE3_CLASS_MEDIASTREAMING = 21,
    # ARCOMMANDS_ID_ARDRONE3_MEDIASTREAMING_CMD_VIDEOENABLE = 0,        
    return struct.pack("BBHB", 1, 21, 0, enable)


def requestAllSettingsCmd():
    # ARCOMMANDS_ID_PROJECT_COMMON = 0,
    # ARCOMMANDS_ID_COMMON_CLASS_SETTINGS = 2,
    # ARCOMMANDS_ID_COMMON_SETTINGS_CMD_ALLSETTINGS = 0
    return struct.pack("BBH", 0, 2, 0)


def requestAllStatesCmd():
    # ARCOMMANDS_ID_PROJECT_COMMON = 0,
    # ARCOMMANDS_ID_COMMON_CLASS_COMMON = 4,
    # ARCOMMANDS_ID_COMMON_COMMON_CMD_ALLSTATES = 0
    return struct.pack("BBH", 0, 4, 0)


def moveCameraCmd( tilt, pan ):
    "Tilt/Pan camera consign for the drone (in degrees)"
    # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
    # ARCOMMANDS_ID_ARDRONE3_CLASS_CAMERA = 1,
    # ARCOMMANDS_ID_ARDRONE3_CAMERA_CMD_ORIENTATION = 0,
    return struct.pack("BBHbb", 1, 1, 0, tilt, pan)


def resetHomeCmd():
    # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1
    # ARCOMMANDS_ID_ARDRONE3_CLASS_GPSSETTINGS = 23
    # ARCOMMANDS_ID_ARDRONE3_GPSSETTINGS_CMD_RESETHOME = 1
    return struct.pack("BBH", 1, 23, 1)

# NOT TESTED - Aldo? Altitude?
def setHomeCmd( lat, lon, altitude=0.0 ):
    # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1
    # ARCOMMANDS_ID_ARDRONE3_CLASS_GPSSETTINGS = 23
    # ARCOMMANDS_ID_ARDRONE3_GPSSETTINGS_CMD_SETHOME = 0,
    return struct.pack("<BBHddd", 1, 23, 0, lat, lon, altitude)

# NOT TESTED - Aldo?
def navigateHomeCmd( go=True ):
    "navigate home - to STOP use go=False"
    # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
    # ARCOMMANDS_ID_ARDRONE3_CLASS_PILOTING = 0,
    # ARCOMMANDS_ID_ARDRONE3_PILOTING_CMD_NAVIGATEHOME = 5,
    return struct.pack("<BBHB", 1, 0, 5, go)


def packData( payload, ackRequest=False ):
    frameType = 2
    if ackRequest:
        frameId = 11
    else:
        frameId = 10
    buf = struct.pack("<BBBI", frameType, frameId, 0, len(payload)+7)
    return buf + payload


class CommandSender( Thread ):
    "it is necessary to send PCMD with fixed frequency - Free Flight uses 40Hz/25ms"
    INTERNAL_COMMAND_PREFIX = chr(0x42)
    EXTERNAL_COMMAND_PREFIX = chr(0x33)
    def __init__( self, commandChannel, hostPortPair ):
        Thread.__init__( self )
        self.setDaemon( True )
        self.shouldIRun = Event()
        self.shouldIRun.set()
        self.lock = Lock()
        self.command = commandChannel
        self.hostPortPair = hostPortPair
        self.seqId = defaultdict( int )
        self.cmd = packData( movePCMDCmd( False, 0, 0, 0, 0 ) )
        assert self.isPCMD( self.cmd )
        self.index = 0
        self.dropIndex = 7 # fake wifi problems

    def updateSeq( self, cmd ):
        "relace sequential byte based on 'channel'"
        assert len(cmd) > 3, repr(cmd)
        frameId = cmd[1]
        self.seqId[ frameId ] += 1
        return cmd[:2] + chr(self.seqId[frameId] % 256) + cmd[3:]

    def isPCMD( self, cmd ):
        if len(cmd) != 7+13: # BBHBbbbbf
            return False
        return struct.unpack("BBH", cmd[7:7+4]) == (1, 0, 2)

    def send( self, cmd ):
        self.lock.acquire()
        self.command.separator( self.EXTERNAL_COMMAND_PREFIX )
        if cmd is not None:
            if self.isPCMD( cmd ):
                self.cmd = cmd
                self.command.separator( cmd ) # just store the command without sending it
            else:
                self.command.sendto( self.updateSeq(cmd), self.hostPortPair )
        self.command.separator( "\xFF" )
        self.lock.release()

    def run( self ):
        while self.shouldIRun.isSet():
            self.index += 1
            if self.dropIndex is None or self.index % self.dropIndex != 0:
                self.lock.acquire()
                self.command.separator( self.INTERNAL_COMMAND_PREFIX )
                self.command.sendto( self.updateSeq(self.cmd), self.hostPortPair )
                self.command.separator( "\xFF" )
                self.lock.release()
            time.sleep(0.025) # 40Hz

class CommandSenderReplay( CommandSender ):
    "fake class to replay synced messages"
    def __init__( self, commandChannel, hostPortPair, checkAsserts=True ):
        CommandSender.__init__( self, commandChannel, hostPortPair )
        self.checkAsserts = checkAsserts

    def start( self ):
        "block default Thread behavior"
        print "STARTED Replay"

    def send( self, cmd ):
        if not self.checkAsserts:
            # ignore input completely
            return

        prefix = self.command.debugRead(1)
        while prefix == self.INTERNAL_COMMAND_PREFIX:
            self.command.separator( self.updateSeq(self.cmd) ) # just verify command identity
            self.command.separator( "\xFF" )
            prefix = self.command.debugRead(1)
        assert prefix == self.EXTERNAL_COMMAND_PREFIX, hex(ord(prefix))

        if cmd is not None:
            if self.isPCMD( cmd ):
                self.cmd = cmd
                self.command.separator( cmd ) # just verify command identity
            else:
                self.command.sendto( self.updateSeq(cmd), self.hostPortPair )
        self.command.separator( "\xFF" )


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    f = open(sys.argv[1], "rb")
    prefix = f.read(1)
    while len(prefix) > 0:
        print hex(ord(prefix))
        assert prefix in [CommandSender.INTERNAL_COMMAND_PREFIX, CommandSender.EXTERNAL_COMMAND_PREFIX]
        term = f.read(1)
        if term != "\xFF":
            header = term + f.read(6)
            frameType, frameId, seqId, totalLen = struct.unpack( "<BBBI", header )
            data = header + f.read( totalLen-7 )
            print " ".join(["%02X" % ord(x) for x in data])
            term = f.read(1)
        else:
            print "EMPTY"
        prefix = f.read(1)


# vim: expandtab sw=4 ts=4 

