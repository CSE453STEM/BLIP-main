#!/usr/bin/python3
# Window on Pi is 62 x 18 (yay)

import curses
import select
import socket
import sys
import os
import time
import signal
import serial

serial_strings = ["","","",""] # index 0 = top of window
sent_strings = ["","","",""] # index 0 = top of window

def rcv_add_top(message):
        serial_strings.pop(0)
        serial_strings.append(message)
        topwin.clrtobot()
        for i in range(0, 4):
                topwin.addnstr(i + 1, 2, serial_strings[i], 58)
        topwin.box()
        topwin.addstr(0,2," Received ", curses.A_REVERSE)
        topwin.refresh()

def send(message):
        sent_strings.pop(0)
        sent_strings.append(message)
        midwin.clrtobot()
        for i in range(0, 4):
                midwin.addnstr(i, 2, sent_strings[i], 58)
        midwin.box()
        midwin.addstr(0,2, " Sent ", curses.A_REVERSE)
        midwin.refresh()

        ser.write(str.encode(message + chr(0xA)))
        ser.flush()
        printer.write(message) # Eventually make a word-wrapping function to encase this probably?
        # Send message to ser port
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
midwin_h = 5
botwin_h = 3
switchwin_h = 3
topwin = curses.newwin(topwin_h, win_w, 0, 0)
topwin.box()
midwin = curses.newwin(midwin_h, win_w, topwin_h, 0)
midwin.box()
switchwin = curses.newwin(switchwin_h, win_w, topwin_h + midwin_h, 0)
switchwin.box()
botwin = curses.newwin(botwin_h, win_w, topwin_h + midwin_h + switchwin_h, 0)
botwin.keypad(1)
botwin.box()
botwin.nodelay(True) # Makes getch() non-blocking
topwin.addstr(0,2," Received ", curses.A_REVERSE)
midwin.addstr(0,2, " Sent ", curses.A_REVERSE)
switchwin.addstr(0,2, " Switch ", curses.A_REVERSE)
botwin.addstr(0,2, " Buffer ", curses.A_REVERSE)

#open communication serial
ser = serial.Serial("/dev/ttyUSB0")	# Should make this configurable in the future
printer = serial.Serial("/dev/ttyAMA0")

inputs = [daemon_sock, ser]	# List of inputs, for select to use
outputs = [ ser ]
s = ""

stdscr.refresh()
topwin.refresh()
midwin.refresh()
switchwin.refresh()
botwin.refresh()

while True:
        c = botwin.getch()
        if c != -1 and c != 0xA and len(s) < 58 and c != 9: #Todo put invalid chars in a collection and check against it
                if c == 263: #backspace
                        s = s[:-1]
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
                send(s) # Appends newline so ser device sends the string
                s = ""
                botwin.clear()
                botwin.box()
                botwin.addstr(0,2, " Buffer ", curses.A_REVERSE)
                botwin.refresh()

        read_ready, write_ready, except_ready = select.select(inputs, outputs, [])
        for r in read_ready:
                if r == ser: #and ser not in write_ready: # Not in write_ready prevents placing string in buffer and then accidentally reading it right back
                        msg = (ser.readline()).decode("utf-8")
                        rcv_add_top(msg)
                        printer.write(msg) # Eventually make a word-wrapping function to encase this probably?
                if r == daemon_sock:
                        botwin.addstr(1,2,daemon_sock.readline().rstrip())
        botwin.refresh()

