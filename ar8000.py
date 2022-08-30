import argparse
import serial
import json


def command(cmd, port='/dev/ttyUSB0', baudrate=9600, timeout=2, quiet=False):

    ser = serial.Serial(
        port, baudrate, stopbits=serial.STOPBITS_TWO, timeout=timeout)

    lines = []
    n = 0
    if type(cmd) is list:
        for cmd_item in cmd:
            ser.write((cmd_item + '\r').encode())
    else:
        ser.write((cmd + '\r').encode())
    if not quiet:
        while True:
            line = ser.read_until().decode()
            new_line = line.replace('\r', '').replace('\n', '')
            if len(new_line) > 0:
                lines.append(new_line)
                n += 1
            if '\r' not in line:
                break
    ser.close()
    return lines


def decode(line):
    items = line.split(' ', 7)
    res = {}
    for item in items:
        if item.startswith('MX'):
            res['memory_bank'] = item[2]
            res['memory_channel'] = item[3:]
        elif item.startswith('MP'):
            res['memory_pass'] = item[2]
        elif item.startswith('RF'):
            res['receive_frequency'] = item[2:]
        elif item.startswith('ST'):
            res['step_increment'] = item[2:]
        elif item.startswith('AU'):
            res['auto_mode'] = item[2]
        elif item.startswith('MD'):
            res['receive_mode'] = item[2]
        elif item.startswith('AT'):
            res['attenuator'] = item[2]
        elif item.startswith('TM'):
            res['display_text'] = item[2:]
    return res


def encode(res):
    return (
        'MX' + res['memory_bank'] + res['memory_channel'] + ' ' +
        'MP' + res['memory_pass'] + ' ' +
        'RF' + res['receive_frequency'] + ' ' +
        'ST' + res['step_increment'] + ' ' +
        'AU' + res['auto_mode'] + ' ' +
        'MD' + res['receive_mode'] + ' ' +
        'AT' + res['attenuator'] + ' ' +
        'TM' + res['display_text']
    )


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-p", "--port", default="/dev/ttyUSB0", help="Serial port")
    argparser.add_argument("-b", "--baud", default=9600,
                           type=int, help="Baud rate")
    argparser.add_argument("-a", "--bank", default='J',
                           type=str, help="Memory bank")
    argparser.add_argument("-t", "--timeout", default='2',
                           type=int, help="Timeout in seconds")
    argparser.add_argument("-r", "--raw", default=False,
                           help="Raw output")
    args = argparser.parse_args()

    port = args.port
    baudrate = args.baud
    memory_bank = args.bank
    timeout = args.timeout

    bank = (command('MA' + memory_bank, port=port,
                    baudrate=baudrate, timeout=timeout))
    if args.raw:
        print(bank)
    else:
        freqs = []
        for freq in bank:
            freqs.append(decode(freq))
        print(json.dumps(freqs, indent=2))
