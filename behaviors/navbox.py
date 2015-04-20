#!/usr/bin/python
"""
  ARDrone3 autonomous landing on ARDrone2 box with Orinted Roundel
  usage:
      !!! WORK IN PROGRESS !!!
       ./navbox.py <task> [<metalog> [<F>]] | --test <image|video> [<stopAt index>]
"""
import sys
import math
import cv2
import os
import numpy as np
import inspect

BEBOP_ROOT = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"..")))
if BEBOP_ROOT not in sys.path:
    sys.path.insert(0, BEBOP_ROOT) # access to drone source without installation

from bebop import Bebop
from commands import movePCMDCmd
from video import navdata2video

from multiprocessing import Process, Queue


# this will be in new separate repository as common library fo robotika Python-powered robots
from apyros.metalog import MetaLog, disableAsserts
from apyros.manual import myKbhit, ManualControlException

TMP_VIDEO_FILE = "video.bin"

g_mser = None

# 14cm x 3cm, 13cm diameter, innner 2cm x 7cm, space between circle and perpendicular line 5cm
def removeDuplicities( rectangles, desiredRatio=14.0/3.0 ):
    "for MSER remove multiple detections of the same strip"
    radius = 30
    ret = []
    for (x,y),(w,h),a in rectangles:
        for (x2,y2),(w2,h2),a2 in ret:
            if abs(x-x2) < radius and abs(y-y2) < radius:
                ratio = max(h,w)/float(min(h,w))
                ratio2 = max(h2,w2)/float(min(h2,w2))
                if abs(ratio-desiredRatio) < abs(ratio2-desiredRatio):
                    # use the bigger one
                    ret.remove( ((x2,y2),(w2,h2),a2) )
                    ret.append( ((x,y),(w,h),a) )
                break
        else:
            ret.append( ((x,y),(w,h),a) )
    return ret

def matchCircRect( circles, rectangles ):
    if len(circles) < 1 or len(rectangles) < 2:
        return None
#    print circles
#    print rectangles
    (centerX, centerY), rad = circles[0]
    rect = [r for r in rectangles if math.hypot(r[0][0]-centerX, r[0][1]-centerY) < 2.1*rad]
    if len(rect) < 2:
        return None
    tmpRect = sorted([(abs(max(r[1][0],r[1][1]) - 2*rad), r) for r in rect])
    return (circles[0][0], tmpRect[0][1][0])

def detectRoundel( frame, debug=False ):
    global g_mser
    global THRESHOLD_FRACTION
    if g_mser == None:
        g_mser = cv2.MSER( _delta = 10, _min_area=100, _max_area=300*50*2 )
    gray = cv2.cvtColor( frame, cv2.COLOR_BGR2GRAY )
    contours = g_mser.detect(gray, None)
    rectangles = []
    circles = []
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        area = len(cnt) # MSER returns all points within area, not boundary points
        rectangleArea = float(rect[1][0]*rect[1][1])
        rectangleAspect = max(rect[1][0], rect[1][1]) / float(min(rect[1][0], rect[1][1]))
        if area/rectangleArea > 0.70 and rectangleAspect > 3.0:
            (x,y),(w,h),angle = rect
            rectangles.append( ((int(x+0.5),int(y+0.5)), (int(w+0.5),int(h+0.5)), int(angle)) )
        cir = cv2.minEnclosingCircle(cnt)
        (x,y),radius = cir
        circleArea = math.pi*radius*radius
        if area/circleArea > 0.64:
            circles.append( ((int(x+0.5),int(y+0.5)),int(radius+0.5)) )
    rectangles = removeDuplicities( rectangles )
    result = matchCircRect( circles=circles, rectangles=rectangles )
    if debug:
        for rect in rectangles:
            box = cv2.cv.BoxPoints(rect)
            box = np.int0(box)
            cv2.drawContours( frame,[box],0,(255,0,0),2)
        for cir in circles:
            (x,y),radius = cir
            center = (int(x),int(y))
            radius = int(radius)
            cv2.circle(frame, center, radius, (0,255,0), 2)
        if result:
            (x1,y1),(x2,y2) = result
            cv2.line(frame, (int(x1),int(y1)), (int(x2),int(y2)), (0,0,255), 3)
    return result


g_index = 0
g_queueOut = None
g_processor = None
g_queueResults = None

def videoCallbackSingleThread( frame, robot=None, debug=False ):
    global g_index
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



def processMain( queueIn, queueOut ):
    debug = False
    for name in os.listdir("."):
        if name.startswith("tmp_") and name.endswith(".jpg"):
            os.remove(name)
    while True:
        frame = queueIn.get()
        if frame is None:
            break
        print "Video", len(frame[-1])
        # workaround for a single frame
        f = open( TMP_VIDEO_FILE, "wb" )
        f.write( frame[-1] )
        f.close()
        cap = cv2.VideoCapture( TMP_VIDEO_FILE )
        ret, img = cap.read()
        cap.release()
        if ret:
            result = detectRoundel( img, debug=debug )
            print result
            cv2.imwrite( "tmp_%03d.jpg" % frame[0], img )
            queueOut.put( (frame[0], result) )
            if debug:
                cv2.imshow('image', img)
                key = cv2.waitKey(200)


def videoCallback( frame, robot=None, debug=False ):
    global g_queueOut, g_processor, g_queueResults
    if g_queueOut is None:
        g_queueOut = Queue()
        g_queueResults = Queue()
        g_processor = Process( target=processMain, args=(g_queueOut,g_queueResults,) )
        g_processor.daemon = True
        g_processor.start()
    g_queueOut.put_nowait( frame ) # H264 compressed video frame

def videoCallbackResults():
    if g_queueResults is None or g_queueResults.empty():
        return None
    return g_queueResults.get()
    




def testCamera( drone ):
    "Collect camera data without takeoff"
    drone.setVideoCallback( videoCallback, videoCallbackResults )
    drone.moveCamera( tilt=-100, pan=0 )
    drone.videoEnable()
    for i in xrange(200):
        print i,
        drone.update( cmd=None )
    if g_queueOut is not None:
        g_queueOut.put_nowait( None )
        g_processor.join()


def testAutomaticLanding( drone ):
    "Takeoff and land"
    drone.setVideoCallback( videoCallback, videoCallbackResults )
    drone.moveCamera( tilt=-100, pan=0 )
    drone.videoEnable()
    try:
        drone.trim()
        drone.takeoff()
        print "COMPLETED", drone.altitude
        prev = drone.lastImageResult
        up = 0
        left = 0
        fwd = 0
        for i in xrange(1000):
            if drone.altitude > 1.5:
                up = -20
            elif drone.altitude < 1.3:
                up = 20
            else:
                up = 0
            print "ALT", drone.altitude, up

            if prev != drone.lastImageResult:
                left, fwd = 0, 0
                print drone.lastImageResult
                prev = drone.lastImageResult
                if drone.lastImageResult is not None:
                    index,result = drone.lastImageResult
                    if result is not None:
                        (centerX,centerY), point = result
                        if centerY < 368/2 - 30:
                            fwd = 20
                        elif centerY > 368/2 + 30:
                            fwd = -20
                        else:
                            fwd = 0
                        if centerX < 640/2 - 30:
                            left = 20
                        elif centerY > 640/2 + 30:
                            left = -20
                        else:
                            left = 0
                        print "HETREERERE!", left, fwd

            print i,
            drone.update( cmd=movePCMDCmd( active=True, roll=left, pitch=fwd, yaw=0, gaz=up ) )
        drone.land()
    except ManualControlException, e:
        print
        print "ManualControlException"
        drone.hover()
        if drone.flyingState is None or drone.flyingState == 1: # taking off
            drone.emergency()
        drone.land()
    if g_queueOut is not None:
        g_queueOut.put_nowait( None )
        g_processor.join()


def replayVideoStream( filename, stopAt=None ):
    "revise only logged video data"
    # convert navdata to video if necessary
    if "navdata" in filename:
        navdata2video( filename, TMP_VIDEO_FILE )
        filename = TMP_VIDEO_FILE        
    cap = cv2.VideoCapture( filename )
    ret, image = cap.read()
    index = 0
    while ret:
        if stopAt is None or index == stopAt:
            result = detectRoundel( image, debug=True )
            print index, result
            pause = 10
            if result:
                pause = 1000
            if index == stopAt:
                pause = 0
            cv2.imshow('image', image)
            key = cv2.waitKey(pause)
            if key >= 0:
                cv2.imwrite( "tmp.jpg", image )
                break
        ret, image = cap.read()
        index += 1
    else:
        key = cv2.waitKey(0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    if sys.argv[1] == "--test":
        filename = sys.argv[2]
        stopAt = None
        if len(sys.argv) > 3:
            stopAt = int(sys.argv[3])
        replayVideoStream( filename=filename, stopAt=stopAt )
        sys.exit(0)

    metalog=None
    if len(sys.argv) > 2:
        metalog = MetaLog( filename=sys.argv[2] )
    if len(sys.argv) > 3 and sys.argv[3] == 'F':
        disableAsserts()

    drone = Bebop( metalog=metalog, onlyIFrames=True )
#    testCamera( drone )
    testAutomaticLanding( drone )
    print "Battery:", drone.battery, "(%.2f, %.2f, %.2f)" % drone.position

# vim: expandtab sw=4 ts=4 

