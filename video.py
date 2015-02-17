#!/usr/bin/python
"""
  Utility for extraction of video stream from navdata log
  usage:
       ./video.py <input navdata log> <output video file>
"""
import sys
import struct
from navdata import cutPacket,videoAckRequired


def navdata2video( inputFile, outputFile ):
    data = open(inputFile, "rb").read()
    arr = []
    while len(data) > 0:
        packet, data = cutPacket( data )
        if videoAckRequired( packet ):
            frameNumber, frameFlags, fragmentNumber = struct.unpack("<HBB", packet[7:11])
            arr.append( (frameNumber, fragmentNumber, packet[12:]) )
    vf = open(outputFile, "wb")
    prev = None
    for a in sorted(arr):
        if prev != a[:2]:
            vf.write(a[2])
        else:
            print "duplicity", prev
        prev = a[:2]
    vf.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print __doc__
        sys.exit(2)
    navdata2video( sys.argv[1], sys.argv[2] )

# vim: expandtab sw=4 ts=4 

