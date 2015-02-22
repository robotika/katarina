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

# vim: expandtab sw=4 ts=4 

