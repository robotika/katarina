import cv2
import time
import sys
import signal

from bebop import Bebop
drone=Bebop()

def main():
    signal.signal(signal.SIGINT, signal_handler)
    try:
        drone.moveCamera(tilt=-50, pan=0)
        drone.videoEnable()

        cap = cv2.VideoCapture('./bebop.sdp')

        while (True):
            ret, img = cap.read()
            if ret:
                cv2.imshow('img', img)
                cv2.namedWindow('img', cv2.WINDOW_NORMAL)
                cv2.waitKey(1)

            drone.update()

        sys.exit(0)
    except (TypeError) as e:
        pass

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

if __name__ == "__main__":
    main()
