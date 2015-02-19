#!/usr/bin/python
"""
  Replay H264 video or directly navdata
  usage:
       ./play.py <input navdata log OR video file>
  
  WARNING: video.bin is used as temporary file
"""
import sys
import cv2
from video import navdata2video

TMP_VIDEO_FILE = "video.bin"

def playVideo( filename ):
    cap = cv2.VideoCapture( filename )
    ret, frame = cap.read()
    #cv2.imwrite( "first-video.jpg", frame )
    while ret:
        cv2.imshow('image', frame)
        cv2.waitKey(100)
        ret, frame = cap.read()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    filename = sys.argv[1]
    if "navdata" in filename:
        navdata2video( filename, TMP_VIDEO_FILE )
        filename = TMP_VIDEO_FILE
    playVideo( filename )

# vim: expandtab sw=4 ts=4 

