#!/usr/bin/python
"""
  ARDrone3 autonomous landing on ARDrone2 box with Orinted Roundel
  usage:
      !!! WORK IN PROGRESS !!!
       ./navbox.py <task> [<metalog> [<F>]]
"""
import sys
import cv2
import numpy as np

sys.path.append('..') # access to drone source without installation

from bebop import Bebop
from commands import movePCMDCmd
from video import VideoFrames

# this will be in new separate repository as common library fo robotika Python-powered robots
from apyros.metalog import MetaLog, disableAsserts
from apyros.manual import myKbhit, ManualControlException

TMP_VIDEO_FILE = "video.bin"

g_mser = None

# 14cm x 3cm, 13cm diameter, innner 2cm x 7cm, space between circle and perpendicular line 5cm

def detectRoundel( frame, debug=False ):
    global g_mser
    global THRESHOLD_FRACTION
    if g_mser == None:
        g_mser = cv2.MSER( _delta = 10, _min_area=100, _max_area=300*50*2 )
    gray = cv2.cvtColor( frame, cv2.COLOR_BGR2GRAY )
    contours = g_mser.detect(gray, None)
    result = []
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
#        print len(cnt), rect
        if len(cnt)/float(rect[1][0]*rect[1][1]) > 0.70:
            result.append( rect )
    if debug:
        for rect in result:
            box = cv2.cv.BoxPoints(rect)
            box = np.int0(box)
            cv2.drawContours( frame,[box],0,(255,0,0),2)
    return result


g_vf = None
g_index = 0

def videoCallback( data, robot=None, debug=False ):
    global g_vf, g_index
    g_vf.append( data )
    frame = g_vf.getFrame()
    if frame:
        print "Video", len(frame)
        # workaround for a single frame
        f = open( TMP_VIDEO_FILE, "wb" )
        f.write( frame )
        f.close()
        cap = cv2.VideoCapture( TMP_VIDEO_FILE )
        ret, img = cap.read()
        cap.release()
        if ret:
            detectRoundel( img, debug=debug )
            if debug:
                cv2.imshow('image', img)
                key = cv2.waitKey(200)
                cv2.imwrite("img_%03d.jpg" % g_index, img)
                g_index += 1
    


def testCamera( drone ):
    "Collect camera data without takeoff"
    global g_vf
    g_vf = VideoFrames( onlyIFrames=True, verbose=False )
    drone.videoCbk = videoCallback
    drone.moveCamera( tilt=-100, pan=0 )
    drone.videoEnable()
    for i in xrange(200):
        print i,
        drone.update( cmd=None )


def testAutomaticLanding( drone ):
    "Takeoff and land"
    global g_vf
#    g_vf = VideoFrames( onlyIFrames=True, verbose=False )
#    drone.videoCbk = videoCallback
    drone.moveCamera( tilt=-100, pan=0 )
    drone.videoEnable()
    try:
        drone.trim()
        drone.takeoff()
#        drone.flyToAltitude( 1.5 )
#        for i in xrange(1000):
#            print i,
#            drone.update( cmd=None )
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
#    testCamera( drone )
    testAutomaticLanding( drone )
    print "Battery:", drone.battery, "(%.2f, %.2f, %.2f)" % drone.position

# vim: expandtab sw=4 ts=4 

