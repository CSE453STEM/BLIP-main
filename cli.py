#!/usr/bin/python3

# Window on Pi is 62 x 18 (yay)

import curses
import select
import socket
import sys
import os
import time
import signal

input_strings = ["","","",""] # index 0 = top of window

def add_top(message):
        input_strings.pop(0)
        input_strings.append(message)
        for i in range(0, 4):
                topwin.clrtobot();
                topwin.box();
                topwin.addnstr(i + 1, 1, input_strings[i], 60)
        topwin.addstr(0,2," Received ", curses.A_REVERSE)
        topwin.refresh()

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
curses.noecho()
curses.cbreak()
stdscr.keypad(1)
curses.curs_set(0)

win_w = 62
topwin_h = 6

midwin_h = 6

botwin_h = 4

topwin = curses.newwin(topwin_h, win_w, 0, 0)
topwin.box()

midwin = curses.newwin(midwin_h, win_w, topwin_h, 0)
midwin.box()

botwin = curses.newwin(botwin_h, win_w, topwin_h + midwin_h + 1, 0)
botwin.box()


topwin.addstr(0,2," Received ", curses.A_REVERSE)
midwin.addstr(0,3, " Sent ", curses.A_REVERSE)
botwin.addstr(0,2, " Buffer ", curses.A_REVERSE)

serial = open("/dev/ttyUSB0", "r")	# Should make this configurable in the future
serial_out = open("/dev/ttyUSB0", "w")	# Should make this configurable in the future

inputs = [daemon_sock, sys.stdin, serial]	# List of inputs, for select to use
outputs = [ serial ]
while True:
        read_ready, write_ready, except_ready = select.select(inputs, outputs, [])
        for r in read_ready:
                if r == serial:
                        add_top(serial.readline().rstrip() )
                if r == daemon_sock:
                        botwin.addstr(1,1,daemon_sock.readline().rstrip())
        #for w in write_ready:
                #Other things
        stdscr.refresh()
        topwin.refresh()
        midwin.refresh()
        botwin.refresh()

