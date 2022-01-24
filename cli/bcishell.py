from serial.tools.list_ports import main as startLister 
from colors import red, green, yellow, color
import curses
import serial
import optparse
import sys
import re
import os
import string


class Main:
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.parser.add_option("-p", "--port", dest="port", help="Use this port", metavar="SERIAL_DEVICE")
        self.parser.add_option("-a", "--mac-address", dest="mac", help="Mac Address to connect to")
        self.parser.add_option("-l", "--list", action="store_true", dest="list", help="List all serial ports")
        self.parser.add_option("-d", "--debug", action="store_true", dest="debug", help="Show Debug Info")
        
        (self.options, self.args) = self.parser.parse_args()

        if self.options.list == True:
            print("Avaiable Ports:")
            sys.argv = [sys.argv[0]]
            startLister()
            exit(0)
        
        if self.options.port == None:
            self.parser.print_help()
            exit()

        if self.options.mac == None:
            self.parser.print_help()
            exit()


        match = re.search(r"^[a-fA-F0-9]{2}(:[a-fA-F0-9]{2}){5}$", self.options.mac)

        if not match:
            print(red(f"E: '{self.options.mac}' is not a vaild mac address"))
            exit()
        
        self.ser = serial.Serial()

        self.ser.port = self.options.port
        self.ser.baudrate = 115200

        try:
            self.ser.open()
        except serial.SerialException:
            print(red("This Port could not be found"))
            exit()

        print(green("I ") + "Waiting for boot signal")

        buf = ""

        while True:
            bytesToRead = self.ser.inWaiting()

            if bytesToRead == 0:
                continue

            buf += self.ser.read(1).decode('UTF-8')

            if buf.endswith('$$$\r\n'):
                if self.options.debug:
                    print(yellow("~~ Begin Debug ~~"))
                    print(buf)
                    print(yellow("~~ End Debug ~~"))
                break
        
        self.scr = curses.initscr()
        curses.start_color()

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        
        buf = "\n" * 1000
        buf += "I: Boot Signal Recieved. Showing Message line...\n"
        buf += " >>> " + self.ser.readline().decode("UTF-8").replace("\r\n", "") + "\n"

        mac_bytes = self.options.mac.split(":")
       
        buf += f"I: Sending Mac Adress {mac_bytes}! \n"

        self.ser.write(bytearray.fromhex(self.options.mac.replace(":", " ") + " 00"))        
        self.ser.flush()
        
        buf += "I: Done! Starting Real Time Transmission\n"
        self.scr.nodelay(True)
        
        titlebar = " BCIShell v1.0 - esc to exit"

        tts = ""
        while True:
            (y, x) = self.scr.getmaxyx()
            
            self.scr.clear()
            self.scr.addstr(0, 0, titlebar + (" " * (x - len(titlebar))), curses.color_pair(2))
            self.scr.addstr(y-2, 0, "> " + tts + (" " * (x - len("> " + tts))), curses.color_pair(2))
           
            bytes_to_read = self.ser.inWaiting()
            if bytes_to_read != 0:
                buf += self.ser.read(bytes_to_read).decode("UTF-8")

            splitbuf = buf.split("\n")

            for i in range(1, y-2):
                s = splitbuf[-i]

                color = curses.color_pair(6)

                if s.startswith("!"):
                    color = curses.color_pair(3)
                
                elif s.startswith("#"):
                    color = curses.color_pair(4)

                elif s.startswith("*"):
                    color = curses.color_pair(5)

                self.scr.addstr(y-(i+2), 1, s, color)

            self.scr.refresh()

            cmd = self.scr.getch()
            if cmd == 27:
                self.end()
                exit()
            if cmd != -1:
                char = chr(cmd)
                if char in string.printable and len(tts) < x - 10 and cmd != 10:
                    tts += char
                elif cmd == 8 and len(tts) > 0:
                    tts = tts[:-1]
                elif cmd == 10:
                    tts += "\n"
                    self.ser.write(tts.encode("UTF-8"))
                    self.ser.flush()
                    buf += "\n > " + tts + "\n"
                    tts = ""

        self.end()

    def end(self):
        curses.endwin()
        self.ser.close()

if __name__ == '__main__':
    Main()

