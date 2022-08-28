import argparse
import serial


argparser = argparse.ArgumentParser()
argparser.add_argument(
    "-p", "--port", default="/dev/ttyUSB0", help="Serial port")
argparser.add_argument("-b", "--baud", default=9600,
                       type=int, help="Baud rate")
argparser.add_argument("-a", "--bank", default='J',
                       type=str, help="Memory bank")
argparser.add_argument("-t", "--timeout", default='2',
                       type=int, help="Timeout in seconds")

args = argparser.parse_args()

port = args.port
baudrate = args.baud
memory_bank = args.bank
timeout = args.timeout


ser = serial.Serial(
    port, baudrate, stopbits=serial.STOPBITS_TWO, timeout=timeout)

ser.write(('\rMA' + memory_bank + '\r').encode())
while True:
    line = ser.readline().decode()
    new_line = line.replace('\r', '').replace('\n', '')
    if len(new_line) > 0:
        print(new_line)
    if '\r' not in line:
        break
