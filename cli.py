#!/usr/bin/python3

# Window on Pi is 62 x 18 (yay)

import curses
import select
import socket
import sys
import os
import time
import signal

serial_strings = ["","","",""] # index 0 = top of window
sent_strings = ["","","",""] # index 0 = top of window

def rcv_add_top(message):
        serial_strings.pop(0)
        serial_strings.append(message)
        topwin.clrtobot()
        topwin.box()
        for i in range(0, 4):
                topwin.addnstr(i + 1, 2, serial_strings[i], 58)
        topwin.addstr(0,2," Received ", curses.A_REVERSE)
        topwin.refresh()

def send(message):
        sent_strings.pop(0)
        sent_strings.append(message)
        midwin.clrtobot()
        for i in range(0, 4):
                midwin.addnstr(i + 1, 2, sent_strings[i], 58)
        midwin.box()
        midwin.addstr(0,3, " Sent ", curses.A_REVERSE)
        midwin.refresh()

        serial_out.write(message + chr(0xA))
        serial.flush()

        # Send message to serial port
        # and display on output log


def end_program():
        curses.curs_set(1)
        curses.nocbreak()
        stdscr.keypad(0)
        curses.echo()
        curses.endwin()
        os.unlink(sock_addr)
        sys.exit(0)

def sigint_handler(signal, frame):
        end_program()

signal.signal(signal.SIGINT, sigint_handler) # Exit gracefully

sock_addr = './unix_socket'

try:
    os.unlink(sock_addr)
except OSError:
    if os.path.exists(sock_addr):
        raise

daemon_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM);

daemon_sock.bind(sock_addr);

daemon_sock.listen(1)	# Listen for connection from daemon


stdscr = curses.initscr()
stdscr.keypad(1)
curses.noecho()
curses.cbreak()
curses.curs_set(0)

win_w = 62
topwin_h = 6

midwin_h = 6

botwin_h = 5

topwin = curses.newwin(topwin_h, win_w, 0, 0)
topwin.box()

midwin = curses.newwin(midwin_h, win_w, topwin_h, 0)
midwin.box()

botwin = curses.newwin(botwin_h, win_w, topwin_h + midwin_h, 0)
botwin.keypad(1)
botwin.box()
botwin.nodelay(True) # Makes getch() non-blocking

topwin.addstr(0,2," Received ", curses.A_REVERSE)
midwin.addstr(0,3, " Sent ", curses.A_REVERSE)
botwin.addstr(0,2, " Buffer ", curses.A_REVERSE)

serial = open("/dev/ttyS3", "r")	# Should make this configurable in the future
serial_out = open("/dev/ttyS3", "w")	# Should make this configurable in the future


inputs = [daemon_sock, serial]	# List of inputs, for select to use
outputs = [ serial ]
s = ""

stdscr.refresh()
topwin.refresh()
midwin.refresh()
botwin.refresh()

while True:

        c = botwin.getch()
        if (c != -1 and c != 0xA and len(s) < 58 and c != 9): #Todo put invalid chars in a collection and check against it
                s = s + chr(c)
        botwin.addstr(2,2, s)

        if (c == 0xA):
                send(s) # Appends newline so serial device sends the string
                s = ""
                botwin.clear()
                botwin.box()
                botwin.addstr(0,2, " Buffer ", curses.A_REVERSE)
                botwin.refresh()

        read_ready, write_ready, except_ready = select.select(inputs, outputs, [])
        for r in read_ready:
                if r == serial: #and serial not in write_ready: # Not in write_ready prevents placing string in buffer and then accidentally reading it right back
                        rcv_add_top(serial.readline().rstrip() )
                if r == daemon_sock:
                        botwin.addstr(1,1,daemon_sock.readline().rstrip())
        #for w in write_ready:
                #Other things
        botwin.refresh()
        
