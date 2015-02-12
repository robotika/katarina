#!/usr/bin/python
"""
  Basic class for communication to Parrot Bebop
  usage:
       ./bebop.py <output directory>
"""
import sys
import socket
import datetime
import struct
from navdata import packData

# hits from https://github.com/ARDroneSDK3/ARSDKBuildUtils/issues/5

HOST = "192.168.42.1"
DISCOVERY_PORT = 44444

NAVDATA_PORT = 43210 # d2c_port
COMMAND_PORT = 54321 # c2d_port

class Bebop:
    def __init__( self ):
        logFilename = datetime.datetime.now().strftime("navdata_%y%m%d_%H%M%S.bin") # TODO metalog
        cmdFilename = datetime.datetime.now().strftime("cmd_%y%m%d_%H%M%S.bin")
        self.navdata = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.navdata.bind( ('',NAVDATA_PORT) )
#        self.navdata.settimeout( SOCKET_TIMEOUT )
        self.command = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.logf = open( logFilename, "wb" )
        self.logCmd = open( cmdFilename, "wb" )

    def update( self, cmd ):
        "send command and return navdata"
        data = None
        while data == None or len(data) == 0:
            data = self.navdata.recv(4094)
            self.logf.write(data)
            self.logf.flush()
        if cmd is not None:
            data = packData( payload=cmd )
            self.logCmd.write( data )
            self.logCmd.flush()
            self.command.sendto( data, (HOST, COMMAND_PORT) )
        self.logCmd.write( "\xFF" ) # remove this when every update will contain valid cmd
        self.logCmd.flush()
        return data


def test( outDir ):
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

    robot = Bebop()
    for i in xrange(10):
        robot.update( cmd=None )
    # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1
    # ARCOMMANDS_ID_ARDRONE3_CLASS_GPSSETTINGS = 23
    # ARCOMMANDS_ID_ARDRONE3_GPSSETTINGS_CMD_RESETHOME = 1
    robot.update( cmd=struct.pack("BBH", 1, 23, 1) )
    for i in xrange(100):
        print i,
        robot.update( cmd=None )

    f.close()
    s.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    test( sys.argv[1] )

# vim: expandtab sw=4 ts=4 

