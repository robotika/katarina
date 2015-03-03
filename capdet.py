#!/usr/bin/python
"""
  The Parrot two color cap detector
  usage:
       ./capdet.py <colors file> <input image>
"""
import sys
import cv2
import numpy as np

rad = 10

def detectTwoColors( img, capColors ):
    imgResult = np.zeros( img.shape, np.uint8 )
    imgB, imgG, imgR = cv2.split(img)
    for col in capColors:
        maskB = np.logical_and( imgB < col[0]+rad, imgB > col[0]-rad )
        maskG = np.logical_and( imgG < col[1]+rad, imgG > col[1]-rad )
        maskR = np.logical_and( imgR < col[2]+rad, imgR > col[2]-rad )
        mask = np.logical_and(maskR, maskG)
        mask = np.logical_and(mask, maskB)
        if col[1] > max(col[0],col[2]):
            imgResult[mask] = (0,255,0) # green
        else:
            imgResult[mask] = (0,128,255) # orange

    gray = cv2.cvtColor( imgResult, cv2.COLOR_BGR2GRAY )
    ret, binary = cv2.threshold( gray, 1, 255, cv2.THRESH_BINARY )

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7))
    binary = cv2.dilate( binary, kernel )
    
    cmpRG = imgR > imgG
    contours, hierarchy = cv2.findContours( binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
    result = []
    for cnt in contours:
        area = cv2.contourArea(cnt, oriented=True)
        if area < 0:
            cv2.drawContours(imgResult, [cnt], -1, (255,0,0), 2)
            maskTmp = np.zeros( (img.shape[0],img.shape[1]), np.uint8 )
            cv2.drawContours(maskTmp, [cnt], -1, 255, -1)
            mask = maskTmp > 0
            orange = np.count_nonzero(np.logical_and( mask, cmpRG ))
            # print abs(area), orange, orange/float(abs(area))
            frac = orange/float(abs(area))
            if abs(area) > 20 and (0.4 < frac < 0.7):
                M = cv2.moments(cnt)
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                result.append( ((cx,cy), int(abs(area)), int(orange)) )

    return imgResult, result


def onmouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        col = img[y][x]
        print col
        capColors.append( col )        
        cv2.imshow('result', detectTwoColors(img, capColors)[0])

def loadColors( filename ):
    capColors = []
    for line in open( filename ):
        line = line.split('#')[0]
        line = line.replace(',',' ').translate(None,"[]")
        if len(line.split()) == 3:
            capColors.append( [int(x) for x in line.split()] )
    return capColors

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
     
    capColors = loadColors( sys.argv[1] )
    filename = sys.argv[2]

    # convert navdata to video if necessary
    from video import navdata2video
    TMP_VIDEO_FILE = "video.bin"
    if "navdata" in filename:
        navdata2video( filename, TMP_VIDEO_FILE )
        filename = TMP_VIDEO_FILE
    
    cap = cv2.VideoCapture( filename )
    ret, img = cap.read()
    cv2.imshow('image', img)    
    cv2.setMouseCallback("image", onmouse)
    pause = 100
    if filename.endswith(".jpg"):
        pause = 0
    while ret:
        cv2.imshow('image', img)    
        cv2.imshow('result', detectTwoColors( img, capColors )[0])
        c = cv2.waitKey( pause )
        if c == 27: # ESC
            break
        if c == 8: # Backspace
            if len(capColors) > 0:
                capColors = capColors[:-1]
        elif c == 32:
            pause = 100 - pause # swap 0 and 100
        else:
            ret, img = cap.read()

    cv2.destroyAllWindows()

# vim: expandtab sw=4 ts=4 

