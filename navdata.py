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
ARNETWORKAL_FRAME_TYPE_DATA_LOW_LATENCY = 0x3
ARNETWORKAL_FRAME_TYPE_DATA_WITH_ACK = 0x4

ARNETWORK_MANAGER_INTERNAL_BUFFER_ID_PING = 0
ARNETWORK_MANAGER_INTERNAL_BUFFER_ID_PONG = 1

POSITION_TIME_DELTA = 0.2 # estimated to 5Hz


def printHex( data ):
    print " ".join(["%02X" % ord(x) for x in data])


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


def parseData( data, robot, verbose=False ):
    # m:\git\ARDroneSDK3\libARNetworkAL\Includes\libARNetworkAL\ARNETWORKAL_Frame.h 
    #   uint8_t type; /**< frame type eARNETWORK_FRAME_TYPE */
    #   uint8_t id; /**< identifier of the buffer sending the frame */
    #   uint8_t seq; /**< sequence number of the frame */
    #   uint32_t size; /**< size of the frame */
    #   uint8_t *dataPtr; /**< pointer on the data of the frame */
    # 
    assert len(data) >= 7, len(data)
    frameType, frameId, frameSeq, frameSize = struct.unpack("<BBBI", data[:7])
    assert frameType in [0x1, 0x2, 0x3, 0x4], frameType # 0x2 = ARNETWORKAL_FRAME_TYPE_DATA, 
                                              # 0x4 = ARNETWORKAL_FRAME_TYPE_DATA_WITH_ACK
    if frameType == ARNETWORKAL_FRAME_TYPE_ACK:
        assert frameSize == 8, frameSize
        assert frameId == 0x8B, hex(frameId)
        if verbose:
            print "ACKACK", ord(data[frameSize-1])
        data = data[frameSize:]
        return data

    if frameType == ARNETWORKAL_FRAME_TYPE_DATA_LOW_LATENCY: # 0x3
        assert frameSize >= 12, frameSize
        assert frameId == 0x7D, hex(frameId)
        frameNumber, frameFlags, fragmentNumber, fragmentsPerFrame = struct.unpack("<HBBB", data[7:12])
        #print "Video", frameNumber, frameFlags, fragmentNumber, fragmentsPerFrame
        #printHex( data[:20] )
        data = data[frameSize:]
        return data

    assert frameId in [0x7F, 0x0, 0x7E], frameId

    if frameId == 0x7F:
        commandProject, commandClass, commandId = struct.unpack("BBH",  data[7:7+4])
        if commandProject == 0:
            if (commandClass, commandId) == (5,7):
                # ARCOMMANDS_ID_PROJECT_COMMON = 0,
                # ARCOMMANDS_ID_COMMON_CLASS_COMMONSTATE = 5,
                # ARCOMMANDS_ID_COMMON_COMMONSTATE_CMD_WIFISIGNALCHANGED = 7,
                rssi = struct.unpack("h", data[7:7+2])[0] # RSSI of the signal between controller and the product (in dbm)
                if verbose:
                    print "Wifi", rssi
            else:
                printHex( data[:frameSize] )
        elif commandProject == 1:
            if (commandClass, commandId) == (4,4):
                lat, lon, alt = struct.unpack("ddd", data[11:11+3*8])
                robot.positionGPS = (lat, lon, alt)
                if verbose:
                    print "Position", lat, lon, alt
            elif (commandClass, commandId) == (4,5):
                speedX, speedY, speedZ = struct.unpack("fff", data[11:11+3*4])
                robot.speed = (speedX, speedY, speedZ)
                robot.position = robot.position[0]+POSITION_TIME_DELTA*speedX, robot.position[1]+POSITION_TIME_DELTA*speedY, robot.position[2]+POSITION_TIME_DELTA*speedZ
                if verbose:
                    print "Speed", speedX, speedY, speedZ
            elif (commandClass, commandId) == (4,6):
                roll, pitch, yaw = struct.unpack("fff", data[11:11+3*4])
                if verbose:
                    print "Angle", roll, pitch, yaw
            elif (commandClass, commandId) == (4,8):
                robot.altitude = struct.unpack("d", data[11:11+8])[0]            
                if verbose:
                    print "Altitude", robot.altitude
            elif (commandClass, commandId) == (25,0):
                tilt,pan = struct.unpack("BB", data[11:11+2])
                if verbose:
                    print "CameraState Tilt/Pan", tilt, pan
            else:
                if verbose:
                    print "UNKNOWN",
                    printHex( data[:frameSize] )
                    assert False
        else:
            print "UNKNOWN Project", commandProject
    elif frameId == 0x7E:
        commandProject, commandClass, commandId = struct.unpack("BBH",  data[7:7+4])
        if (commandProject, commandClass) == (0,3):
            # ARCOMMANDS_ID_COMMON_CLASS_SETTINGSSTATE = 3,
            if commandId == 0:
                # ARCOMMANDS_ID_COMMON_SETTINGSSTATE_CMD_ALLSETTINGSCHANGED = 0
                if verbose:
                    print "AllSettings - done."
            elif commandId == 2:
                # ARCOMMANDS_ID_COMMON_SETTINGSSTATE_CMD_PRODUCTNAMECHANGED = 2
                if verbose:
                    print "ProductName", data[11:frameSize-1]
            elif commandId == 3:
                # ARCOMMANDS_ID_COMMON_SETTINGSSTATE_CMD_PRODUCTVERSIONCHANGED = 3
                if verbose:
                    print "ProductVersion", data[11:frameSize-1]
            elif commandId == 4:
                # ARCOMMANDS_ID_COMMON_SETTINGSSTATE_CMD_PRODUCTSERIALHIGHCHANGED = 4
                if verbose:
                    print "ProductSerialHigh", data[11:frameSize-1]
            elif commandId == 5:
                # ARCOMMANDS_ID_COMMON_SETTINGSSTATE_CMD_PRODUCTSERIALLOWCHANGED = 5
                if verbose:
                    print "ProductSerialLow", data[11:frameSize-1]
            elif commandId == 6:
                # ARCOMMANDS_ID_COMMON_SETTINGSSTATE_CMD_COUNTRYCHANGED = 6
                if verbose:
                    print "Country", data[11:frameSize-1]                    
            elif commandId == 7:
                # ARCOMMANDS_ID_COMMON_SETTINGSSTATE_CMD_AUTOCOUNTRYCHANGED = 7
                if verbose:
                    print "AutoCountry", struct.unpack("B", data[11:12])[0]
            else:
                if verbose:
                    print "Unknown(0,3)", commandId
                    printHex( data[:frameSize] )
        elif (commandProject, commandClass, commandId) == (0,5,1):
            battery = struct.unpack("B", data[11:12])[0]
            robot.battery = battery
            if verbose:
                print "Battery", battery
        elif (commandProject, commandClass, commandId) == (0,5,4):
            if verbose:
                print "Date:", data[11:frameSize-1]
        elif (commandProject, commandClass, commandId) == (0,5,5):
            if verbose:
                print "Time:", data[11:frameSize-1]
        elif (commandProject, commandClass, commandId) == (0,10,0):
            # ARCOMMANDS_ID_COMMON_CLASS_WIFISETTINGSSTATE = 10,
            # ARCOMMANDS_ID_COMMON_WIFISETTINGSSTATE_CMD_OUTDOORSETTINGSCHANGED
            if verbose:
                print "WiFi Outdoor:", struct.unpack("B", data[11:12])[0]
        elif (commandProject, commandClass) == (0,14):
            # ARCOMMANDS_ID_COMMON_CLASS_CALIBRATIONSTATE = 14,
            if commandId == 0:
                # ARCOMMANDS_ID_COMMON_CALIBRATIONSTATE_CMD_MAGNETOCALIBRATIONSTATECHANGED = 0,
                x,y,z,failed = struct.unpack("BBBB", data[11:11+4])
                if verbose:
                    print "Magnetometer calibration", (x,y,z), failed
            elif commandId == 1:
                # ARCOMMANDS_ID_COMMON_CALIBRATIONSTATE_CMD_MAGNETOCALIBRATIONREQUIREDSTATE
                required = struct.unpack("B", data[11:11+1])[0]
                if verbose:
                    print "Magnetometer calibration required", required
            elif commandId == 3:
                # ARCOMMANDS_ID_COMMON_CALIBRATIONSTATE_CMD_MAGNETOCALIBRATIONSTARTEDCHANGED
                started = struct.unpack("B", data[11:11+1])[0]
                if verbose:
                    print "Magnetometer calibration required", started
            else:
                if verbose:
                    print "Calibration", commandId,
                    printHex( data[:frameSize] )

        elif (commandProject, commandClass) == (1,4):
            # ARCOMMANDS_ID_ARDRONE3_CLASS_PILOTINGSTATE = 4,
            if commandId == 0:
                # ARCOMMANDS_ID_ARDRONE3_PILOTINGSTATE_CMD_FLATTRIMCHANGED = 0
                print "FlatTrim changed"
                robot.flatTrimCompleted = True
            elif commandId == 1:
                # ARCOMMANDS_ID_ARDRONE3_PILOTINGSTATE_CMD_FLYINGSTATECHANGED = 1
                state = struct.unpack("I", data[11:11+4])[0]
                states = ["landed", "takingoff", "hovering", "flying", "landing", "emergency"]
                robot.flyingState = state
                print "Flying State", state, states[state]
            elif commandId == 2:
                # ARCOMMANDS_ID_ARDRONE3_PILOTINGSTATE_CMD_ALERTSTATECHANGED
                state = struct.unpack("I", data[11:11+4])[0]
                states = ["none/No alert", "user/User emergency alert", "cut_out/Cut out alert", "critical_battery", "low_battery", "too_much_angle"]
                print "ALERT State", state, states[state]
            elif commandId == 3:
                # ARCOMMANDS_ID_ARDRONE3_PILOTINGSTATE_CMD_NAVIGATEHOMESTATECHANGED
                state, reason = struct.unpack("II", data[11:11+2*4])
                states = ["available", "inProgress", "unavailable", "pending", "low_battery", "too_much_angle"]
                reasons = ["userRequest", "connectionLost", "lowBattery", "finished", "stopped", "disabled", "enabled"]
                print "NavigateHomeStateChanged", state, states[state], reasons[reason]
                robot.navigateHomeState = state
            else:
                print "Unknown Piloting State", commandId,
                printHex( data[:frameSize] )

        elif (commandProject, commandClass) == (1,6):
            # ARCOMMANDS_ID_ARDRONE3_CLASS_PILOTINGSETTINGSSTATE = 6,
            if commandId == 0:
                # ARCOMMANDS_ID_ARDRONE3_PILOTINGSETTINGSSTATE_CMD_MAXALTITUDECHANGED = 0,
                if verbose:
                    print "MaxAltitude:", struct.unpack("fff", data[11:11+3*4])
            elif commandId == 1:
                # ARCOMMANDS_ID_ARDRONE3_PILOTINGSETTINGSSTATE_CMD_MAXTILTCHANGED = 1,
                if verbose:
                    print "MaxTilt:", struct.unpack("fff", data[11:11+3*4])
            elif commandId == 2:
                # ARCOMMANDS_ID_ARDRONE3_PILOTINGSETTINGSSTATE_CMD_ABSOLUTCONTROLCHANGED,
                if verbose:
                    print "AbsoluteControl:", struct.unpack("B", data[11:12])[0]
            else:
                print "Unknown Piloting Settings State", commandId,
                printHex( data[:frameSize] )

        elif (commandProject, commandClass, commandId) == (1,8,0):
            # ARCOMMANDS_ID_ARDRONE3_CLASS_MEDIARECORDSTATE = 8,
            # ARCOMMANDS_ID_ARDRONE3_MEDIARECORDSTATE_CMD_PICTURESTATECHANGED = 0,
            if verbose:
                state, massStorageId = struct.unpack("BB", data[11:11+2])
                print "Picture State Changed:", state, massStorageId

        elif (commandProject, commandClass, commandId) == (1,8,1):
            # ARCOMMANDS_ID_ARDRONE3_CLASS_MEDIARECORDSTATE = 8,
            # ARCOMMANDS_ID_ARDRONE3_MEDIARECORDSTATE_CMD_VIDEOSTATECHANGED = 1
            if verbose:
                state, massStorageId = struct.unpack("IB", data[11:11+4+1])
                states = ["stopped", "started", "failed", "autostopped"]
                print "Video State Changed:", states[state], massStorageId

        elif (commandProject, commandClass) == (1,12):
            # ARCOMMANDS_ID_ARDRONE3_CLASS_SPEEDSETTINGSSTATE
            #  ARCOMMANDS_ID_ARDRONE3_SPEEDSETTINGSSTATE_CMD_MAXVERTICALSPEEDCHANGED = 0,
            #  ARCOMMANDS_ID_ARDRONE3_SPEEDSETTINGSSTATE_CMD_MAXROTATIONSPEEDCHANGED,
            #  ARCOMMANDS_ID_ARDRONE3_SPEEDSETTINGSSTATE_CMD_HULLPROTECTIONCHANGED,
            #  ARCOMMANDS_ID_ARDRONE3_SPEEDSETTINGSSTATE_CMD_OUTDOORCHANGED,
            pass

        elif (commandProject, commandClass) == (1,16):
            # ARCOMMANDS_ID_ARDRONE3_CLASS_SETTINGSSTATE = 16,
            if commandId == 4:
                # ARCOMMANDS_ID_ARDRONE3_SETTINGSSTATE_CMD_MOTORFLIGHTSSTATUSCHANGED = 4,
                nbFlights, lastFlightDuration, totalFlightDuration = struct.unpack("HHI", data[11:11+8])
                if verbose:
                    print "Motor flights status", nbFlights, lastFlightDuration, totalFlightDuration
            elif commandId == 5:
                # ARCOMMANDS_ID_ARDRONE3_SETTINGSSTATE_CMD_MOTORERRORLASTERRORCHANGED = 5
                lastError = struct.unpack("I", data[11:11+4])[0]
                if verbose:
                    print "Motor last error", lastError
            else:
                if verbose:
                    print "Settings state", commandId,
                    printHex( data[:frameSize] )

        elif (commandProject, commandClass, commandId) == (1,20,5):
            # ARCOMMANDS_ID_ARDRONE3_CLASS_PICTURESETTINGSSTATE = 20,            
            if verbose:
                print "VIDEOAUTORECORDCHANGED", struct.unpack("BB", data[11:11+2])

        elif (commandProject, commandClass, commandId) == (1,22,0):
            # ARCOMMANDS_ID_ARDRONE3_CLASS_MEDIASTREAMINGSTATE = 22,
            # ARCOMMANDS_ID_ARDRONE3_MEDIASTREAMINGSTATE_CMD_VIDEOENABLECHANGED = 0,
            state = struct.unpack("I", data[11:11+4])[0]
            states = ["enabled", "disabled", "error"]
            if verbose:
                print "Video Enabled State", state, states[state]

        elif (commandProject, commandClass, commandId) == (1,24,0):
            # ARCOMMANDS_ID_ARDRONE3_CLASS_GPSSETTINGSSTATE = 24,
            # ARCOMMANDS_ID_ARDRONE3_GPSSETTINGSSTATE_CMD_HOMECHANGED = 0,
            if verbose:
                print "Home changed", struct.unpack("dd", data[11:11+16])

        elif (commandProject, commandClass, commandId) == (1,24,2):
            # ARCOMMANDS_ID_ARDRONE3_CLASS_GPSSETTINGSSTATE = 24,
            # ARCOMMANDS_ID_ARDRONE3_GPSSETTINGSSTATE_CMD_GPSFIXSTATECHANGED = 2,
            if verbose:
                print "GPSFixStateChanged - fixed:", struct.unpack("B", data[11:11+1])

        elif (commandProject, commandClass, commandId) == (129,3,0):
            if verbose:
                print "GPSDebugState, numSat =", struct.unpack("B", data[11:11+1])[0]

        elif commandProject == 129:
            if verbose:
                print "DEBUG",
                printHex( data[:frameSize] )
        else:
            if verbose:
                print "Unknown ACK:",
                printHex( data[:frameSize] )
    elif frameId == 0x0: # ARNETWORK_MANAGER_INTERNAL_BUFFER_ID_PING
        assert frameSize == 15, len(data)
        seconds, nanoseconds = struct.unpack("<II", data[7:15])
        assert nanoseconds < 1000000000, nanoseconds
        timestamp = seconds + nanoseconds/1000000000.
        robot.time = timestamp
        if verbose:
            print "Time" , timestamp
    data = data[frameSize:]
    return data


def ackRequired( data ):
    return parseFrameType( data ) == ARNETWORKAL_FRAME_TYPE_DATA_WITH_ACK


def createAckPacket( data ):
    assert len(data) >= 7, len(data)
    frameType, frameId, frameSeq, frameSize = struct.unpack("<BBBI", data[:7])
    assert frameType == 0x4, frameType
    assert len(data) == frameSize, (len(data), frameSize)

    # get the acknowledge sequence number from the data
#    payload = data[7:8] # strange
    payload = struct.pack("B", frameSeq)
#    payload = struct.pack("B", 1)
#    print "ACK", repr(payload)

    frameType = ARNETWORKAL_FRAME_TYPE_ACK
    frameId = 0xFE # 0x7E + 0x80
    buf = struct.pack("<BBBI", frameType, frameId, 0, len(payload)+7)
    return buf + payload


def pongRequired( data ):
    if len(data) < 7:
        return False
    frameType, frameId, frameSeq, frameSize = struct.unpack("<BBBI", data[:7])
    return frameId == ARNETWORK_MANAGER_INTERNAL_BUFFER_ID_PING

def createPongPacket( data ):
    assert len(data) >= 7, len(data)
    frameType, frameId, frameSeq, frameSize = struct.unpack("<BBBI", data[:7])
    assert frameType == 0x2, frameType
    assert frameId == ARNETWORK_MANAGER_INTERNAL_BUFFER_ID_PING, frameId
    assert len(data) == frameSize, (len(data), frameSize)

    payload = data[7:]
    frameType = 2
    frameId = ARNETWORK_MANAGER_INTERNAL_BUFFER_ID_PONG
    buf = struct.pack("<BBBI", frameType, frameId, 0, len(payload)+7)
    return buf + payload


def videoAckRequired( data ):
    if len(data) < 7:
        return False
    frameType, frameId, frameSeq, frameSize = struct.unpack("<BBBI", data[:7])
    return frameType == ARNETWORKAL_FRAME_TYPE_DATA_LOW_LATENCY and frameId == 0x7D

g_currentVideoFrameNumber = None
g_lowPacketsAck = 0
g_highPacketsAck = 0

def createVideoAckPacket( data ):
    global g_currentVideoFrameNumber, g_lowPacketsAck, g_highPacketsAck

    assert len(data) >= 12, len(data)
    frameNumber, frameFlags, fragmentNumber, fragmentsPerFrame = struct.unpack("<HBBB", data[7:12])

    if frameNumber != g_currentVideoFrameNumber:
        g_lowPacketsAck = 0
        g_highPacketsAck = 0
        g_currentVideoFrameNumber = frameNumber

    if fragmentNumber < 64:
        g_lowPacketsAck |= (1<<fragmentNumber)
    else:
        g_highPacketsAck |= (1<<(fragmentNumber-64))
    

    payload = struct.pack("<HQQ", frameNumber, g_highPacketsAck, g_lowPacketsAck )
    frameType = 2
    frameId = 13
    buf = struct.pack("<BBBI", frameType, frameId, 0, len(payload)+7)
    return buf + payload



class DummyRobot:
    position = (0,0,0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    robot = DummyRobot()
    data = open(sys.argv[1], "rb").read()
    while data:
        data = parseData( data, robot, verbose=True )

# vim: expandtab sw=4 ts=4 

