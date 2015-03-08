"""
  Encode Parrot Bebop commands
"""
import struct

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
    return struct.pack("BBHBbbbbf", 1, 0, 2, flag, roll, pitch, yaw, gaz, psi )


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

# vim: expandtab sw=4 ts=4 

