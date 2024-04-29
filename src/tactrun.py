import RPi.GPIO as GPIO
import time
import sys, os

if __name__ == "__main__":
	# GPIO

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	print("Waiting...")

	while True:
		button1 = GPIO.input(3)
		button2 = GPIO.input(2)
		cmd = ""
		if button1 == False and button2 == True:
			cmd = "python3 /root/testpy/mini2.py"
		if button1 == False and button2 == False:
			cmd = "python3 /root/testpy/mini2_contours_Xfps.py"
		if cmd != "":
			ret = os.popen(cmd).readline().strip()
			print(ret)
			time.sleep(1)
		time.sleep(0.1)
	GPIO.cleanup()
