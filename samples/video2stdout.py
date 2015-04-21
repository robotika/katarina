#!/usr/bin/python
"""
  Minimal example how to stream video to ffplay
  usage:
       ./video2stdout.py | ffplay -
"""
import sys
import os
import inspect

# http://stackoverflow.com/questions/10020325/make-python-stop-emitting-a-carriage-return-when-writing-newlines-to-sys-stdout
if sys.platform == "win32":
   import msvcrt
   msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

BEBOP_ROOT = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"..")))
if BEBOP_ROOT not in sys.path:
    sys.path.insert(0, BEBOP_ROOT) # access to drone source without installation
from bebop import Bebop

def videoCallback( frame, robot=None, debug=False ):
    sys.stdout.write( frame[-1] ) # ignore frameNumber and frameFlag
    sys.stdout.flush()


def video2stdout():
    drone = Bebop( metalog=None, onlyIFrames=False )
    drone.videoCbk = videoCallback
    drone.videoEnable()
    while True:
        drone.update()

if __name__ == "__main__":
    video2stdout()

# vim: expandtab sw=4 ts=4 

