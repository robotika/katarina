#!/usr/bin/python
"""
  Parsing of incomming messages from Parrot Bebop
  usage:
       ./navdata.py <logged file>
"""
import sys
import struct

def printHex( data ):
    print " ".join(["%02X" % ord(x) for x in data])

def parseData( data ):
    # m:\git\ARDroneSDK3\libARNetworkAL\Includes\libARNetworkAL\ARNETWORKAL_Frame.h 
    #   uint8_t type; /**< frame type eARNETWORK_FRAME_TYPE */
    #   uint8_t id; /**< identifier of the buffer sending the frame */
    #   uint8_t seq; /**< sequence number of the frame */
    #   uint32_t size; /**< size of the frame */
    #   uint8_t *dataPtr; /**< pointer on the data of the frame */
    # 
    assert len(data) >= 7+4, len(data)
    frameType, frameId, frameSeq, frameSize = struct.unpack("<BBBI", data[:7])
    assert frameType == 0x2, frameType # 0x2 = ARNETWORKAL_FRAME_TYPE_DATA
    assert frameId in [0x7F, 0x0], frameId
    assert frameSize in [15, 19, 23, 35], frameSize
    if frameId == 0x7F:
        commandProject, commandClass, commandId = struct.unpack("BBH",  data[7:7+4])
        assert commandProject == 1, commandProject
        if (commandClass, commandId) == (4,4):
            lat, lon, alt = struct.unpack("ddd", data[11:11+3*8])
            print "Position", lat, lon, alt
        if (commandClass, commandId) == (4,5):
            speedX, speedY, speedZ = struct.unpack("fff", data[11:11+3*4])
            print "Speed", speedX, speedY, speedZ
        if (commandClass, commandId) == (4,6):
            roll, pitch, yaw = struct.unpack("fff", data[11:11+3*4])
            print "Angle", roll, pitch, yaw
        if (commandClass, commandId) == (4,8):
            altitude = struct.unpack("d", data[11:11+8])[0]
            print "Altitude", altitude
    data = data[frameSize:]
    return data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    data = open(sys.argv[1], "rb").read()
    while data:
        data = parseData( data )

# vim: expandtab sw=4 ts=4 

