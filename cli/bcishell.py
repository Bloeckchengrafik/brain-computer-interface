import serial
import optparse

class Main:
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.parser.add_option("-p", "--port", dest="port", help="Use this port", metavar="FILE")
        
        (self.options, self.args) = self.parser.parse_args()

        if self.options.port == None:
            self.parser.print_help()
            exit(0)

        self.ser = serial.Serial()

        self.ser.port = self.options.port
        self.ser.baudrate = 115200

        self.ser.open()
        print("Begin Init")
        while self.ser.readline() != b'$$$\r\n':
            pass
        print("Start Data")
        print(self.ser.readline().decode("UTF-8").replace("\r\n", ""))

        mac_to_send = input("Mac to connect to: ")
        mac_bytes = mac_to_send.split(":")
        
        for b in mac_bytes:
            self.ser.write(int(b, 16))
        
        self.ser.flush()
        
        print("Done! Starting Real Time Transmission")

        try:
            while True:
                bytesToRead = self.ser.inWaiting()

                if bytesToRead == 0:
                    continue

                print(self.ser.read(bytesToRead).decode('UTF-8'), end='')

        except KeyboardInterrupt:
            pass
        self.ser.close()
if __name__ == '__main__':
    Main()
