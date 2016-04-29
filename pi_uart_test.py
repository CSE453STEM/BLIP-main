#!/usr/bin/env python3

import serial

print("Testing UART. Sending \"Hello World\" to serial port at 19200bps...")

uart = serial.Serial("/dev/ttyAMA0", baudrate=19200, timeout=3.0)

uart.write("Hello, world!\n")

print("Done.")
