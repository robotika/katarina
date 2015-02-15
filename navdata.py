#!/usr/bin/python
"""
  Parsing of incomming messages from Parrot Bebop
  usage:
       ./navdata.py <logged file>
"""
import sys
import struct

ARNETWORKAL_FRAME_TYPE_ACK = 0x1
ARNETWORKAL_FRAME_TYPE_DATA = 0x2 
ARNETWORKAL_FRAME_TYPE_DATA_WITH_ACK = 0x4

ARNETWORK_MANAGER_INTERNAL_BUFFER_ID_PING = 0
ARNETWORK_MANAGER_INTERNAL_BUFFER_ID_PONG = 1

g_seq = 1
g_seqAck = 1
g_seqPongAck = 1

def printHex( data ):
    print " ".join(["%02X" % ord(x) for x in data])


def packData( payload ):
    global g_seq
    frameType = 2
    frameId = 10 # up to 127? no idea
    frameSeq = g_seq
    g_seq += 1
    buf = struct.pack("<BBBI", frameType, frameId, frameSeq % 256, len(payload)+7)
    return buf + payload

def parseFrameType( data ):
    if len(data) < 7:
        return None
    frameType, frameId, frameSeq, frameSize = struct.unpack("<BBBI", data[:7])
    assert len(data) == frameSize, (len(data), frameSize)
    return frameType

def cutPacket( data ):
    if len(data) < 7:
        return None, data
    frameType, frameId, frameSeq, frameSize = struct.unpack("<BBBI", data[:7])
    return data[:frameSize], data[frameSize:]


def parseData( data ):
    # m:\git\ARDroneSDK3\libARNetworkAL\Includes\libARNetworkAL\ARNETWORKAL_Frame.h 
    #   uint8_t type; /**< frame type eARNETWORK_FRAME_TYPE */
    #   uint8_t id; /**< identifier of the buffer sending the frame */
    #   uint8_t seq; /**< sequence number of the frame */
    #   uint32_t size; /**< size of the frame */
    #   uint8_t *dataPtr; /**< pointer on the data of the frame */
    # 
    assert len(data) >= 7, len(data)
    frameType, frameId, frameSeq, frameSize = struct.unpack("<BBBI", data[:7])
    assert frameType in [0x1, 0x2, 0x4], frameType # 0x2 = ARNETWORKAL_FRAME_TYPE_DATA, 
                                              # 0x4 = ARNETWORKAL_FRAME_TYPE_DATA_WITH_ACK
    if frameType == ARNETWORKAL_FRAME_TYPE_ACK:
        assert frameSize == 8, frameSize
        assert frameId == 0x8B, hex(frameId)
        print "ACKACK", ord(data[frameSize-1])
        data = data[frameSize:]
        return data

    assert frameId in [0x7F, 0x0, 0x7E], frameId
    assert frameSize in [12, 15, 19, 23, 35], frameSize

    if frameId == 0x7F:
        commandProject, commandClass, commandId = struct.unpack("BBH",  data[7:7+4])
        assert commandProject == 1, commandProject
        if (commandClass, commandId) == (4,4):
            lat, lon, alt = struct.unpack("ddd", data[11:11+3*8])
            print "Position", lat, lon, alt
        elif (commandClass, commandId) == (4,5):
            speedX, speedY, speedZ = struct.unpack("fff", data[11:11+3*4])
            print "Speed", speedX, speedY, speedZ
        elif (commandClass, commandId) == (4,6):
            roll, pitch, yaw = struct.unpack("fff", data[11:11+3*4])
            print "Angle", roll, pitch, yaw
        elif (commandClass, commandId) == (4,8):
            altitude = struct.unpack("d", data[11:11+8])[0]
            print "Altitude", altitude
        else:
            print "UNKNOWN",
            printHex( data[:frameSize] )
            assert False
    elif frameId == 0x7E:
        commandProject, commandClass, commandId = struct.unpack("BBH",  data[7:7+4])
        if (commandProject, commandClass, commandId) == (0,5,1):
            battery = struct.unpack("B", data[11:12])[0]
            print "Battery", battery
        else:
            printHex( data[:frameSize] )
    elif frameId == 0x0: # ARNETWORK_MANAGER_INTERNAL_BUFFER_ID_PING
        assert frameSize == 15, len(data)
        seconds, nanoseconds = struct.unpack("<II", data[7:15])
        assert nanoseconds < 1000000000, nanoseconds
        timestamp = seconds + nanoseconds/1000000000.
        print "Time" , timestamp
    data = data[frameSize:]
    return data


def ackRequired( data ):
    return parseFrameType( data ) == ARNETWORKAL_FRAME_TYPE_DATA_WITH_ACK


def createAckPacket( data ):
    global g_seqAck

    assert len(data) >= 7, len(data)
    frameType, frameId, frameSeq, frameSize = struct.unpack("<BBBI", data[:7])
    assert frameType == 0x4, frameType
    assert len(data) == frameSize, (len(data), frameSize)

    # get the acknowledge sequence number from the data
#    payload = data[7:8] # strange
    payload = struct.pack("B", frameSeq)
#    payload = struct.pack("B", 1)
    print "ACK", repr(payload)

    frameType = 0x4
    frameId = 11
    frameSeq = g_seqAck
    g_seqAck += 1
    buf = struct.pack("<BBBI", frameType, frameId, frameSeq % 256, len(payload)+7)
    return buf + payload


def pongRequired( data ):
    if len(data) < 7:
        return False
    frameType, frameId, frameSeq, frameSize = struct.unpack("<BBBI", data[:7])
    return frameId == ARNETWORK_MANAGER_INTERNAL_BUFFER_ID_PING

def createPongPacket( data ):
    global g_seqPongAck
    assert len(data) >= 7, len(data)
    frameType, frameId, frameSeq, frameSize = struct.unpack("<BBBI", data[:7])
    assert frameType == 0x2, frameType
    assert frameId == ARNETWORK_MANAGER_INTERNAL_BUFFER_ID_PING, frameId
    assert len(data) == frameSize, (len(data), frameSize)

    payload = data[7:]
    frameType = 2
    frameId = ARNETWORK_MANAGER_INTERNAL_BUFFER_ID_PONG
    frameSeq = g_seqPongAck
    g_seqPongAck += 1
    buf = struct.pack("<BBBI", frameType, frameId, frameSeq % 256, len(payload)+7)
    return buf + payload


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    data = open(sys.argv[1], "rb").read()
    while data:
        data = parseData( data )

# vim: expandtab sw=4 ts=4 

