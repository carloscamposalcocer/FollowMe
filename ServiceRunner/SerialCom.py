import glob
import sys
from time import time, sleep
import serial
import logging

logger = logging.getLogger(__name__)

class Ardu:
    def __init__(self):
        ports = serial_ports()
        self.ser = serial.Serial(ports[0], 115200, timeout=10)
        start_message = self.readline()
        logger.info(start_message)
        assert start_message.startswith("Ready")
        logger.info("Connected, ready to send commands")

    def readline(self):
        return self.ser.readline().decode()

    def send(self, X, Y):
        # X = max(min(X, 2300), 700)
        # Y = max(min(Y, 2300), 700)
        X = int(X + 1500)
        Y = int(-Y + 1500)
        b = [113, 4, X % 256, X // 256, Y % 256, Y // 256]
        b = bytearray(b)
        # print(f"Sending Message:X->{X} Y->{Y}")
        self.ser.write(b)
        # print(f"Waiting for Response...")
        message = self.readline()
        if message.startswith("Donne"):
            message = message.strip("\n").strip("\r")
            # print(message)
        else:
            logger.error("Error message failed")

    def close(self):
        self.send(0, 0)
        logger.info("Sended 0, 0")
        self.ser.close()


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


if __name__ == '__main__':
    ardu = Ardu()
    while True:
        print(f"send 1500")
        ardu.send(1500, 1500)
        sleep(3)
        print("send 500")
        ardu.send(1000, 2000)
        sleep(3)
        print("send -500")
        ardu.send(2000, 1000)
        sleep(3)
