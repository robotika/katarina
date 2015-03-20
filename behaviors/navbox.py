#!/usr/bin/python
"""
  ARDrone3 autonomous landing on ARDrone2 box with Orinted Roundel
  usage:
      !!! WORK IN PROGRESS !!!
       ./navbox.py <task> [<metalog> [<F>]] | --test <image>
"""
import sys
import math
import cv2
import numpy as np

sys.path.append('..') # access to drone source without installation

from bebop import Bebop
from commands import movePCMDCmd
from video import VideoFrames

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
    rad = circles[0][1]
    tmpRect = sorted([(abs(max(r[1][0],r[1][1]) - 2*rad), r) for r in rectangles])
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
        if area/circleArea > 0.70:
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


g_vf = None
g_index = 0
g_queueOut = None
g_processor = None

def videoCallbackSingleThread( data, robot=None, debug=False ):
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



def processMain( queue ):
    debug = False
    while True:
        frame = queue.get()
        if frame is None:
            break
        print "Video", len(frame)
        # workaround for a single frame
        f = open( TMP_VIDEO_FILE, "wb" )
        f.write( frame )
        f.close()
        cap = cv2.VideoCapture( TMP_VIDEO_FILE )
        ret, img = cap.read()
        cap.release()
        if ret:
            print detectRoundel( img, debug=debug )
            if debug:
                cv2.imshow('image', img)
                key = cv2.waitKey(200)


def videoCallback( data, robot=None, debug=False ):
    global g_vf, g_queueOut, g_processor
    g_vf.append( data )
    frame = g_vf.getFrame()
    if frame:
        if g_queueOut is None:
            g_queueOut = Queue()
            g_processor = Process( target=processMain, args=(g_queueOut,) )
            g_processor.daemon = True
            g_processor.start()
        g_queueOut.put_nowait( frame ) # H264 compressed video frame




def testCamera( drone ):
    "Collect camera data without takeoff"
    global g_vf
    g_vf = VideoFrames( onlyIFrames=True, verbose=False )
    drone.videoCbk = videoCallback
#    drone.videoCbk = videoCallbackSingleThread
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
    global g_vf
    g_vf = VideoFrames( onlyIFrames=True, verbose=False )
    drone.videoCbk = videoCallback
    drone.moveCamera( tilt=-100, pan=0 )
    drone.videoEnable()
    try:
        drone.trim()
        drone.takeoff()
        drone.flyToAltitude( 1.5 )
        print "COMPLETED", drone.altitude
        for i in xrange(1000):
            print i,
            drone.hover()
        drone.land()
    except ManualControlException, e:
        print
        print "ManualControlException"
        if drone.flyingState is None or drone.flyingState == 1: # taking off
            drone.emergency()
        drone.land()
    if g_queueOut is not None:
        g_queueOut.put_nowait( None )
        g_processor.join()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    if sys.argv[1] == "--test":
        image = cv2.imread( sys.argv[2] )
        detectRoundel( image, debug=True )
        cv2.imshow('image', image)
        key = cv2.waitKey(0)
        sys.exit(0)

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

