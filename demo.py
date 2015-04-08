#!/usr/bin/python
"""
  ARDrone3 demo with autonomous navigation to two color Parrot Cap
  usage:
       ./demo.py <task> [<metalog> [<F>]]
"""
import sys
import cv2

from bebop import Bebop
from commands import movePCMDCmd
from capdet import detectTwoColors, loadColors

# this will be in new separate repository as common library fo robotika Python-powered robots
from apyros.metalog import MetaLog, disableAsserts
from apyros.manual import myKbhit, ManualControlException

TMP_VIDEO_FILE = "video.bin"


def videoCallback( frame, robot=None, debug=False ):
    if frame:
        print "Video", len(frame)
        # workaround for a single frame
        f = open( TMP_VIDEO_FILE, "wb" )
        f.write( frame[-1] )
        f.close()
        cap = cv2.VideoCapture( TMP_VIDEO_FILE )
        ret, img = cap.read()
        cap.release()
        if ret:
            detImg, detected = detectTwoColors( img, loadColors("cap-colors.txt") )
            print "Detected", detected
            if len(detected) > 0:
                target = detected[0]
                for alt in detected[1:]:
                    if alt[1] > target[1]: # area
                        target = alt
                print "Target", target, img.shape
                cv2.circle( img, target[0], 20, (255,0,0), 3)
                if robot:
                    diff = target[0][0] - 320
                    if diff < 0:
#                        robot.moveCamera( robot.cameraTilt, robot.cameraPan - 1 )
                        robot.update( movePCMDCmd(active=True, roll=0, pitch=0, yaw=-10, gaz=0) )
                    elif diff > 0:
#                        robot.moveCamera( robot.cameraTilt, robot.cameraPan + 1 )
                        robot.update( movePCMDCmd(active=True, roll=0, pitch=0, yaw=+10, gaz=0) )
            if debug:
                cv2.imshow('image', img)
                key = cv2.waitKey(200)
    


def demo0( drone ):
    print "Follow 2-color cap ..."
    drone.videoCbk = videoCallback
    drone.videoEnable()
    for i in xrange(1000):
        print i,
        drone.update( cmd=None )


def demo( drone ):
    print "Follow 2-color cap ..."
    drone.videoCbk = videoCallback
    drone.videoEnable()
    try:
        drone.trim()
        drone.takeoff()
        drone.flyToAltitude( 1.5 )
        for i in xrange(1000):
            print i,
            drone.update( cmd=None )
        drone.land()
    except ManualControlException, e:
        print
        print "ManualControlException"
        if drone.flyingState is None or drone.flyingState == 1: # taking off
            drone.emergency()
        drone.land()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    metalog=None
    if len(sys.argv) > 2:
        metalog = MetaLog( filename=sys.argv[2] )
    if len(sys.argv) > 3 and sys.argv[3] == 'F':
        disableAsserts()

    drone = Bebop( metalog=metalog )
    demo( drone )
    print "Battery:", drone.battery

# vim: expandtab sw=4 ts=4 

