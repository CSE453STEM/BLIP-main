#!/usr/bin/python3

import curses
import select
import sys
import os
import time
import signal
import textwrap
import serial


s = "" # The unambiguously named string for what's in the input buffer
switchchar = '0' # Global variables!

################################################################################
#   rcv_add_top:
#   Reads a string in from the BLIP serial connection and displays it at the
#   bottom of the receive window.
################################################################################
serial_strings = ["","","",""] # index 0 = top of window
sent_strings = ["","","",""] # index 0 = top of window

def rcv_add_top(message):
        # Rotate old string out, place new one in
        serial_strings.pop(0)
        serial_strings.append(message)
        # Clear window, print messages, refresh window
        topwin.clrtobot()
        for i in range(0, 4):
                topwin.addnstr(i + 1, 2, serial_strings[i], 58)
        topwin.box()
        topwin.addstr(0,2," Received ", curses.A_REVERSE)
        topwin.refresh()
        message = "<< " + message
        lines = textwrap.wrap(message, 32) # Wrap at 32 chars for printer
        for line in lines:
                printer_ser.write(str.encode(line + chr(0xA)))
                printer_ser.flush()


################################################################################
#   update_char:
#   Updates the information about the character on the toggles.
################################################################################
def update_char(newchar):
        switchchar = newchar
        switchwin.addstr(1,15, switchchar)
        switchwin.addstr(1,18, switchchar)
        switchwin.refresh()


################################################################################
#   send:
#   Takes a message, logs it on the printer, and then formats it for the BLIP
#   TCU, finally sending it over the serial port.
################################################################################
def send(message):
        sent_strings.pop(0)
        sent_strings.append(message)
        midwin.clrtobot()
        for i in range(0, 4):
                midwin.addnstr(i, 2, sent_strings[i], 58)
        midwin.box()
        midwin.addstr(0,2, " Sent ", curses.A_REVERSE)
        midwin.refresh()

        blip_ser.write(str.encode(message + chr(0xA)))
        blip_ser.flush()

        message = ">> " + message
        lines = textwrap.wrap(message, 62)

        for line in lines:
                printer_ser.write(str.encode(line + chr(0xA)))
                printer_ser.flush()


################################################################################
#   pushbutton:
#   Adds the character on the toggles to the input buffer if it's a printable
#   character and there's room in the buffer.
#   TODO: does string.printable work for sanity checking?
#   Also, the string in the input buffer is only named 's'. Needs refactoring
################################################################################
def pushbutton():
        if len(s) < 58 and switchchar in string.printable:
            s = s + switchchar
            botwin.clear()
            botwin.box()
            botwin.addstr(1,2, s)
            botwin.refresh()


################################################################################
#   read_switches:
#   Reads an 8-character string from the Arduino and handles input from
#   switches and pushbutton
#   Behavior will probably be odd if you hold the pushbutton and flip switches
#   but it shouldn't really hurt anything(tm)
################################################################################
def read_switches():
        switchbits = switch_ser.readline().rstrip() # Read line, strip \n
        charval = 0;
        # If top bit is set, pushbutton is active. Handle, then strip MSB
        if (int(switchbits, 2) >= 128):
            pushbutton()
            switchbits = '0' + switchbits[1:]
        return chr(int(switchbits, 2))



################################################################################
#   end_program:
#   Implements a graceful, UNIX-y exit for when the program is terminated.
################################################################################
def end_program():
        # Graceful exit, restoring terminal and cleaning up
        curses.curs_set(1)
        curses.nocbreak()
        stdscr.keypad(0)
        curses.echo()
        curses.endwin()
        blip_ser.close()
        printer_ser.close()
        sys.exit(0)


################################################################################
#   sigint_handler:
#   Allows the program to catch Control-C (SIGKILL) and exit nicely.
################################################################################
def sigint_handler(signal, frame):
        end_program()
signal.signal(signal.SIGINT, sigint_handler) # Exit gracefully on ^C


################################################################################
#   Set up basic curses objects and options
################################################################################
stdscr = curses.initscr()
stdscr.keypad(1)
curses.noecho()
curses.cbreak()
curses.curs_set(0)

################################################################################
#   Set up all the gross objects for curses windows
################################################################################
win_w = 62
topwin_h = 6
midwin_h = 5
botwin_h = 3
switchwin_h = 3

topwin = curses.newwin(topwin_h, win_w, 0, 0)
topwin.box()
topwin.addstr(0,2," Received ", curses.A_REVERSE)

midwin = curses.newwin(midwin_h, win_w, topwin_h, 0)
midwin.box()
midwin.addstr(0,2, " Sent ", curses.A_REVERSE)

switchwin = curses.newwin(switchwin_h, win_w, topwin_h + midwin_h, 0)
switchwin.addstr(0,2, " Switches ", curses.A_REVERSE)
switchwin.addstr(1,5, "Character:")

botwin = curses.newwin(botwin_h, win_w, topwin_h + midwin_h + switchwin_h, 0)
botwin.keypad(1)
botwin.box()
botwin.nodelay(True) # Makes getch() non-blocking for this window
botwin.addstr(0,2, " Buffer ", curses.A_REVERSE)
 
stdscr.refresh()
topwin.refresh()
midwin.refresh()
switchwin.refresh()
botwin.refresh()

################################################################################
# Set up serial communications                                                 #
################################################################################
blip_ser = serial.Serial("/dev/ttyUSB0", baudrate=19200)

printer_ser = serial.Serial("/dev/ttyAMA0", baudrate=19200)
try:
        printer_ser.close()
except:
        pass
printer_ser.open() # Is this needed?

switch_ser = serial.Serial("/dev/ttyACM0", baudrate=19200)
try:
        switch_ser.close()
except:
        pass
switch_ser.open()


################################################################################
# Set up Select to handle multiple inputs
################################################################################
inputs = [switch_ser, blip_ser]	# List of inputs, for select to use
outputs = []


while True:
        c = botwin.getch() # Non blocking: returns -1 if no char available
        if c != -1 and c != 0xA and len(s) < 58 and c != 9:
                if c == 263: #backspace
                        s = s[:-1] # Drop last char of string
                        botwin.clear()
                        botwin.box()
                        botwin.addstr(0,2, " Buffer ", curses.A_REVERSE)
                        botwin.addstr(1,2,s)
                        botwin.refresh()
                else:
                        #s = s + str(ord(chr(c)))
                        s = s + chr(c)
                        botwin.addstr(1,2, s)
        
        elif c == 0xA:
                send(s) # Appends newline so blip_ser device sends the string
                s = ""
                botwin.clear()
                botwin.box()
                botwin.addstr(0,2, " Buffer ", curses.A_REVERSE)
                botwin.refresh()

        read_ready, write_ready, except_ready = select.select(inputs, outputs, [])
        for r in read_ready:
                if r == blip_ser:
                        msg = blip_ser.readline().decode("utf-8")
                        rcv_add_top(msg)
                if r == switch_ser:
                        global switchchar 
                        switchchar = read_switches()
                        update_char(switchchar)
        botwin.refresh()

