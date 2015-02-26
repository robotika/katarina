#!/usr/bin/python
"""
  The Parrot two color cap detector
  usage:
       ./capdet.py <input image> [<colors file>]
"""
import sys
import cv2
import numpy as np

imgResult = None
imgR,imgG,imgR = None, None, None
rad = 10

def addColor( col ):
    maskB = np.logical_and( imgB < col[0]+rad, imgB > col[0]-rad )
    maskG = np.logical_and( imgG < col[1]+rad, imgG > col[1]-rad )
    maskR = np.logical_and( imgR < col[2]+rad, imgR > col[2]-rad )
    mask = np.logical_and(maskR, maskG)
    mask = np.logical_and(mask, maskB)
    if col[1] > max(col[0],col[2]):
        imgResult[mask] = (0,255,0) # green
    else:
        imgResult[mask] = (0,128,255) # orange

def onmouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        col = img[y][x]
        print x,y, col
        imgResult[y][x]=255
        addColor( col )
        cv2.imshow('result', imgResult)


def detectTwoColors( img, colorA, colorB ):
    cv2.imshow('image', img)
    img2 = cv2.cvtColor( img, cv2.COLOR_RGB2HSV )
    cv2.imshow('hsv', img2)

    gray = cv2.cvtColor( imgResult, cv2.COLOR_BGR2GRAY )
    ret, binary = cv2.threshold( gray, 1, 255, cv2.THRESH_BINARY )

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7))
    binary = cv2.dilate( binary, kernel )
    
    cmpRG = imgR > imgG
    contours, hierarchy = cv2.findContours( binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
    for cnt in contours:
        area = cv2.contourArea(cnt, oriented=True)
        if area < 0:
            cv2.drawContours(imgResult, [cnt], -1, (255,0,0), 2)
            maskTmp = np.zeros( (img.shape[0],img.shape[1]), np.uint8 )
            cv2.drawContours(maskTmp, [cnt], -1, 255, -1)
            mask = maskTmp > 0
            orange = np.count_nonzero(np.logical_and( mask, cmpRG ))
            print abs(area), orange, orange/float(abs(area))
    cv2.imshow('result', imgResult)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    filename = sys.argv[1]
    img = cv2.imread( filename )
    imgResult = np.zeros( img.shape, np.uint8 )
    imgB, imgG, imgR = cv2.split(img)
     
    if len(sys.argv) > 2:
        for line in open(sys.argv[2]):
            line = line.split('#')[0]
            line = line.replace(',',' ').translate(None,"[]")
            if len(line.split()) == 3:
                addColor( [int(x) for x in line.split()] )

    detectTwoColors( img, None, None )
    cv2.setMouseCallback("image", onmouse)    
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# vim: expandtab sw=4 ts=4 

