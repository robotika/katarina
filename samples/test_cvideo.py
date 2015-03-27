#!/usr/bin/python
"""
  Test of video streaming via cvideo + OpenCV
  usage:
       ./test_cvideo.py <note> [<metalog> [<F>]]
"""
import sys

sys.path.append('..') # access to drone source without installation
from bebop import Bebop
from video import VideoFrames
from apyros.metalog import MetaLog, disableAsserts
from apyros.manual import myKbhit, ManualControlException

from multiprocessing import Process, Queue

import cvideo
import numpy as np
import cv2

g_vf = None
g_queueOut = None
g_processor = None

def processMain( queue ):
    cvideo.init()
    img = np.zeros([360,640,3], dtype=np.uint8)    

    while True:
        frame = queue.get()
        if frame is None:
            break
        sys.stderr.write('.')
        ret = cvideo.frame( img, 1, frame )
        assert ret
        cv2.imshow('image', img)
        key = cv2.waitKey(100)
        if key >= 0:
            break


def videoCallback( data, robot=None, debug=False ):
    global g_vf, g_queueOut, g_processor
    if g_vf is None:
        g_vf = VideoFrames( onlyIFrames=True, verbose=False )
    g_vf.append( data )
    frame = g_vf.getFrame()
    if frame:
        if g_queueOut is None:
            g_queueOut = Queue()
            g_processor = Process( target=processMain, args=(g_queueOut,) )
            g_processor.daemon = True
            g_processor.start()
        g_queueOut.put_nowait( frame ) # H264 compressed video frame


def testCVideo( drone ):
    drone.videoCbk = videoCallback
    drone.videoEnable()
    for i in xrange(1000):
        drone.update()
    if g_queueOut is not None:
        g_queueOut.put_nowait( None )
        g_processor.join()


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
    testCVideo( drone )

# vim: expandtab sw=4 ts=4 

