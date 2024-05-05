#!/usr/bin/env python3

import time
import cv2
import ST7789


# Create a display instance
disp = ST7789.ST7789(
        height=240,
        width=240,
        rotation=0,
        port=0,
        cs=0,
        rst=5,
        dc=6,
        backlight=13,
        spi_speed_hz=80 * 1000 * 1000
)

# Display Initialize
print('Disp Init...')
disp._spi.mode = 3
disp.reset()
disp._init()

# Capture Initialize
print('Capture Init...')
#cap = cv2.VideoCapture('/dev/video0',cv2.CAP_V4L2)
cap = cv2.VideoCapture('/root/mov/mov.mp4')
if (cap.isOpened()== False):
    print("ERROR:Read mov")

while(cap.isOpened()):

    ret, frame = cap.read()
    if ret == True:
        #Rotate
        frame = cv2.rotate(frame,cv2.ROTATE_90_COUNTERCLOCKWISE)
        #Flip LR
        frame = cv2.flip(frame,0)

        #Output
        disp.display(frame)
    else:
        break


cap.release()
cv2.destroyAllWindows()
disp.reset()
disp._init()
exit()
