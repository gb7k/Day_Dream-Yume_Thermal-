#!/usr/bin/env python3

import time
import cv2
import numpy as np
import ST7789

np.set_printoptions(threshold=np.inf)

#GPIO Initialize
import RPi.GPIO as GPIO

color : int = 1
blightness : int = 50

#sw19 = 19
#sw26 = 26
sw21 = 21


'''
def my_callback2(sw26):
    global blightness
    if blightness == 100:
        blightness = 100
        backlight_pin.ChangeDutyCycle(blightness)
    else:
        blightness = blightness + 10
        backlight_pin.ChangeDutyCycle(blightness)

def my_callback3(sw19):
    global blightness
    if blightness == 10:
        blightness = 10
        backlight_pin.ChangeDutyCycle(blightness)
    else:
        blightness = blightness - 10
        backlight_pin.ChangeDutyCycle(blightness)
'''
def my_callback4(sw21):
    global color
    color = color + 1

#GPIO Initialize
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)  #04_Exit App
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP) #23_Red
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP) #24_Green
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP) #25_Blue
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP) #19_Dark
#GPIO.add_event_detect(sw19, GPIO.RISING, callback=my_callback3, bouncetime=200)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP) #26_Light
#GPIO.add_event_detect(sw26, GPIO.RISING, callback=my_callback2, bouncetime=200)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP) #21_Black,White
GPIO.add_event_detect(sw21, GPIO.RISING, callback=my_callback4, bouncetime=200)

sw_statusR = GPIO.input(23)
sw_statusG = GPIO.input(24)
sw_statusB = GPIO.input(25)

GPIO.setup(13, GPIO.OUT)
backlight_pin = GPIO.PWM(13, 500)
backlight_pin.start(blightness)
# Create a display instance
disp = ST7789.ST7789(
        height=240,
        width=240,
        rotation=0,
        port=0,
        cs=0,
        rst=5,
        dc=6,
        #backlight=13,
        spi_speed_hz=96 * 1000 * 1000
)

# Display Initialize
print('Disp Init...')
disp._spi.mode = 3
disp.reset()
disp._init()

# Capture Initialize
print('Capture Init...')
cap = cv2.VideoCapture('/dev/video0',cv2.CAP_V4L2)

cap_width : int = 256;
cap_height : int = 192;
cap_fps : int = 25;
cap.set(cv2.CAP_PROP_FRAME_WIDTH, cap_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_height)
cap.set(cv2.CAP_PROP_FPS, cap_fps)
cap.set(cv2.CAP_PROP_CONVERT_RGB,0)
cap.set(cv2.CAP_PROP_SETTINGS, 0)

IR_Scale_MAX: int = 5700;
IR_Scale_MIN: int = 5300;

# Start Capture
print('Capture Start')
while(cap.isOpened()):
    #time0=time.time()
    ret, frame = cap.read()

    if ret == True:
        #time1=time.time()
        # Convert (196,256,2) -> (196,256)
        image_r = np.take(frame,[0],axis=2).astype(np.uint16)+np.take(frame,[1],axis=2).astype(np.uint16)*255
        image = image_r.reshape(192,256)

        # Crop 256x196 -> 192x192
        #image = image[0:192,32:224]       #2.8-12mm Lens
        #image = image[0:192,0:256]        #2.5mm 2.8mm Lens
        #image = image[193:384,0:256]      #P2 Pro Raw

        if 1 == 1:
            # use Contrast Adjust
            #if 0 White Hot  if 1 Black Hot
            min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(image)

            IR_Scale_MAX = min_val - 20
            IR_Scale_MIN = max_val
            
            if color % 2 == 0:
                IR_Scale_MAX = min_val - 20
                IR_Scale_MIN = max_val
            else:
                IR_Scale_MAX = max_val - 20
                IR_Scale_MIN = min_val

            alpha = 256.0 / (IR_Scale_MAX - IR_Scale_MIN)
            beta = alpha * IR_Scale_MIN * -1
            image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        else:
            # not use Contrast Adjust 
            if color % 2 == 1:
                image = cv2.bitwise_not(image)

        #Rotate
        image = cv2.rotate(image,cv2.ROTATE_180)
        #Flip LR
        image = cv2.flip(image,0)

        #Add Border                       L  R  T  B
        #image = cv2.copyMakeBorder(image, 5,60,50,86, cv2.BORDER_CONSTANT, value=[0,0,0])  #2.5mm Lens
        #image = cv2.copyMakeBorder(image,10,55,65,65, cv2.BORDER_CONSTANT, value=[0,0,0])  #2.8mm Lens
        image = cv2.copyMakeBorder(image,20,25,50,50, cv2.BORDER_CONSTANT, value=[0,0,0])  #2.8mm Lens P2 Pro
        #Resize 240x240
        image = cv2.resize(image,(240,240))

        #convert GrayScale -> RGB
        image = cv2.cvtColor(image,cv2.COLOR_GRAY2RGB)

        #Color Convert
        #Red
        if sw_statusR == 1:
            image[:, :, 0] = 0
        #Green
        if sw_statusG == 1:
            image[:, :, 1] = 0
        #Blue
        if sw_statusB == 1:
            image[:, :, 2] = 0

        disp.display(image)

        #Time Measurement
        #time2=time.time()
        #print(time2-time0)
        #print('{:.4f}'.format((time2-time0)))

        sw_status4 = GPIO.input(4)    # Break
        sw_status26 = GPIO.input(26)  # Light
        sw_status19 = GPIO.input(19)  # Dark

        if sw_status4 == 0:
            print('BREAK!')
            cap.release()
            cv2.destroyAllWindows()
            disp.reset()
            disp._init()
            backlight_pin.stop()
            GPIO.cleanup()
            exit()

        if sw_status26 == 0:
            if blightness == 100:
                blightness = 100
            else:
                blightness = blightness + 2
                backlight_pin.ChangeDutyCycle(blightness)

        if sw_status19 == 0:
            if blightness <= 2:
                blightness = 2
            else:
                blightness = blightness - 2
                backlight_pin.ChangeDutyCycle(blightness)

print('Error')
cap.release()
cv2.destroyAllWindows()
GPIO.cleanup()
exit()
