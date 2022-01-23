from serial.tools.list_ports import main as startLister 
from colors import red, green, yellow, color
import curses
import serial
import optparse
import sys
import re
import os


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
        
        self.ser = serial.Serial()

        self.ser.port = self.options.port
        self.ser.baudrate = 115200

        self.scr = curses.initscr()
        curses.start_color()

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)

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
        
        print(green("I ") + "Boot Signal Recieved. Showing Message line...")
        print(red(" >>> ") + self.ser.readline().decode("UTF-8").replace("\r\n", ""))

        mac_to_send = self.options.mac
        
        match = re.search(r"^[a-fA-F0-9]{2}(:[a-fA-F0-9]{2}){5}$", mac_to_send)

        if not match:
            print(red(f"E: '{mac_to_send}' is not a vaild mac address"))
            exit()

        mac_bytes = match.string.split(":")
        
        for b in mac_bytes:
            self.ser.write(bytes(int(b, 16)))
        
        self.ser.flush()
        
        print(green("I ") + "Done! Starting Real Time Transmission")
        
        x = self.scr.getmaxyx()[0]
        
        titlebar = " BCIShell v1.0 "

        buf = "\n" * 1000
        while True:
            (x, y) = self.scr.getmaxyx()
            
            self.scr.clear()
            self.scr.addstr(0, 0, titlebar + (" " * (y - len(titlebar))), curses.color_pair(2))
            
            self.scr.refresh()
            self.scr.nodelay(True)

            cmd = self.scr.getch()

            self.scr.addstr(10, 3, str(cmd))
            if cmd != -1:
                if cmd == curses.KEY_END:
                    self.end()
                    return

        try:
            buf = "\n"
            while True:
                bytesToRead = self.ser.inWaiting()

                if bytesToRead == 0:
                    continue

                print(yellow(self.ser.read(1).decode('UTF-8')), end="")
        except KeyboardInterrupt:
            print(red("\nStopping Transmission..."))
        
        self.end()

    def end(self):
        curses.endwin()
        self.ser.close()

if __name__ == '__main__':
    Main()
