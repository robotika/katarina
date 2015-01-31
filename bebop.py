#!/usr/bin/python
"""
  Basic class for communication to Parrot Bebop
  usage:
       ./bebop.py <output directory>
"""
import sys
import socket

# hits from https://github.com/ARDroneSDK3/ARSDKBuildUtils/issues/5

HOST = "192.168.42.1"
DISCOVERY_PORT = 44444

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
    f.close()
    s.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    test( sys.argv[1] )

# vim: expandtab sw=4 ts=4 

