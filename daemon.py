#!/usr/bin/python3

import RPi.GPIO as GPIO
import signal, sys, time
import socket, os
def Exit_gracefully(signal, frame):
    GPIO.cleanup()
    try:
        daemon_sock.close()
    except:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, Exit_gracefully)


GPIO.setmode(GPIO.BCM)

toggles = [4,14,15,18,17,27,22] #Follows physical order on board
push    = 23

# TODO
# Store byte on switches in a global
# and send it as a char through the socket each time
# a change occurs.
#
# Will require changing each interrupt handler (bit0, etc)
# and assembling a byte from bits in the report function.


sock_addr = './unix_socket'
def report(msg):
    if os.path.exists(sock_addr):
        char = 0
        bits = [
        for i in range(0,6):
            
        daemon_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        daemon_sock.connect(sock_addr)
        daemon_sock.send(msg)
        daemon_sock.close()
#    else:
#        print("No socket")

def bit0(channel):
    b = GPIO.input(4) # Determine if high or low now
    report("0" + str(b)) # Send string
def bit1(channel):
    b = GPIO.input(4) 
    report("1" + str(b)) 
def bit2(channel):
    b = GPIO.input(4) 
    report("2" + str(b)) 
def bit3(channel):
    b = GPIO.input(4) 
    report("3" + str(b)) 
def bit4(channel):
    b = GPIO.input(4) 
    report("4" + str(b)) 
def bit5(channel):
    b = GPIO.input(4) 
    report("5" + str(b)) 
def bit6(channel):
    b = GPIO.input(4) 
    report("0" + str(b)) 
        
def pushbtn(channel):
    report("p")

for i in toggles: # Set toggleswitch pins to input, set pulldowns
    GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Set interrupt listeners (probably exists a neater way?)
GPIO.add_event_detect( 4, GPIO.BOTH, callback=bit0, bouncetime=350)
GPIO.add_event_detect(14, GPIO.BOTH, callback=bit1, bouncetime=350)
GPIO.add_event_detect(15, GPIO.BOTH, callback=bit2, bouncetime=350)
GPIO.add_event_detect(18, GPIO.BOTH, callback=bit3, bouncetime=350)
GPIO.add_event_detect(17, GPIO.BOTH, callback=bit4, bouncetime=350)
GPIO.add_event_detect(27, GPIO.BOTH, callback=bit5, bouncetime=350)
GPIO.add_event_detect(22, GPIO.BOTH, callback=bit6, bouncetime=350)
GPIO.add_event_detect(23, GPIO.BOTH, callback=pushbtn)

while True:
    pass

