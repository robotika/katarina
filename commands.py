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


    # TODO:
    # ARCOMMANDS_ID_ARDRONE3_PILOTING_CMD_PCMD = 2,


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


def videoRecording( on=True ):
    # ARCOMMANDS_ID_PROJECT_ARDRONE3 = 1,
    # ARCOMMANDS_ID_ARDRONE3_CLASS_MEDIARECORD = 7,
    # ARCOMMANDS_ID_ARDRONE3_MEDIARECORD_CMD_VIDEO = 1
    massStorageId = 0 # internal ??
    if on:
        return struct.pack("BBHBB", 1, 7, 1, 1, massStorageId)
    else:
        return struct.pack("BBHBB", 1, 7, 1, 0, massStorageId)


# vim: expandtab sw=4 ts=4 

