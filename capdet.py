#!/usr/bin/python
"""
  The Parrot two color cap detector
  usage:
       ./capdet.py <input image>
"""
import sys
import cv2
import numpy as np

imgResult = None
imgR,imgG,imgR = None, None, None
rad = 10

def onmouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        col = img[y][x]
        print x,y, col
        imgResult[y][x]=255
        maskB = np.logical_and( imgB < col[0]+rad, imgB > col[0]-rad )
        maskG = np.logical_and( imgG < col[1]+rad, imgG > col[1]-rad )
        maskR = np.logical_and( imgR < col[2]+rad, imgR > col[2]-rad )
        mask = np.logical_and(maskR, maskG)
        mask = np.logical_and(mask, maskB)
        if col[1] > max(col[0],col[2]):
            imgResult[mask] = (0,255,0) # green
        else:
            imgResult[mask] = (0,128,255) # orange
        cv2.imshow('result', imgResult)


def detectTwoColors( img, colorA, colorB ):
    cv2.imshow('image', img)
    img2 = cv2.cvtColor( img, cv2.COLOR_RGB2HSV )
    cv2.imshow('hsv', img2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    filename = sys.argv[1]
    img = cv2.imread( filename )
    imgResult = np.zeros( img.shape, np.uint8 )
    imgB, imgG, imgR = cv2.split(img)
    detectTwoColors( img, None, None )
    cv2.setMouseCallback("image", onmouse)    
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# vim: expandtab sw=4 ts=4 

