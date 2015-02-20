#!/usr/bin/python
"""
  Utility for extraction of video stream from navdata log
  usage:
       ./video.py <input navdata log> <output video file> [<output frames directory>]
"""
import sys
import struct
import os
from navdata import cutPacket,videoAckRequired


def navdata2video( inputFile, outputFile, outDir = ".", dumpIndividualFrames=False, startIndex=0 ):
    data = open(inputFile, "rb").read()
    arr = []
    while len(data) > 0:
        packet, data = cutPacket( data )
        if videoAckRequired( packet ):
            frameNumber, frameFlags, fragmentNumber = struct.unpack("<HBB", packet[7:11])
            arr.append( (frameNumber, fragmentNumber, packet[12:]) )
    vf = open(outputFile, "wb")
    prev = None
    frameIndex = startIndex
    frame = ""
    for a in sorted(arr):
        if prev != a[:2]:
            if prev is not None and prev[0] != a[0]:
                # new frame
                if dumpIndividualFrames:
                    fout = open(outDir+os.sep+"frame%04d.bin" % frameIndex, "wb")
                    fout.write(frame)
                    fout.close()                    
                frame = ""
                frameIndex += 1
            frame += a[2]
            vf.write(a[2])
        else:
            print "duplicity", prev
        prev = a[:2]
    vf.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print __doc__
        sys.exit(2)
    if len(sys.argv) == 3:
        navdata2video( sys.argv[1], sys.argv[2] )
    else:
        outDir = sys.argv[3]
        startIndex = len(os.listdir( outDir ))
        navdata2video( sys.argv[1], sys.argv[2], outDir=outDir, dumpIndividualFrames=True, startIndex=startIndex )

# vim: expandtab sw=4 ts=4 

