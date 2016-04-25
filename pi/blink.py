#!/usr/bin/python3

import RPi.GPIO as GPIO
import time

pin = 4

GPIO.setmode(BCM)
GPIO.setup(pin, GPIO.OUT)

while True:
        GPIO.output(pin, GPIO.LOW)
        time.sleep(1)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(1)

