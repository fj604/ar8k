
import json
import serial
import serial.tools.list_ports

from guizero import App, Window, Text, TextBox, MenuBar, Combo, PushButton, select_file


freqs = []
timeout = 2


def decode(line):
    items = line.split(' ', 7)
    res = {}
    for item in items:
        if item.startswith('---'):
            return None
        elif item.startswith('MX'):
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
        'MD' + res['receive_mode'] + ' ' +
        'AT' + res['attenuator'] + ' ' +
        'TM' + res['display_text']
    )


def update_freqs_display(data):
    global freqs
    p = 0
    for freq in data:
        freqs[p]['memory_bank'].clear()
        freqs[p]['memory_bank'].append(freq['memory_bank'])
        freqs[p]['memory_channel'].clear()
        freqs[p]['memory_channel'].append(freq['memory_channel'])
        freqs[p]['memory_pass'].clear()
        freqs[p]['memory_pass'].append(freq['memory_pass'])
        freqs[p]['receive_frequency'].clear()
        freqs[p]['receive_frequency'].append(freq['receive_frequency'])
        freqs[p]['step_increment'].clear()
        freqs[p]['step_increment'].append(freq['step_increment'])
        freqs[p]['receive_mode'].clear()
        freqs[p]['receive_mode'].append(freq['receive_mode'])
        freqs[p]['attenuator'].clear()
        freqs[p]['attenuator'].append(freq['attenuator'])
        freqs[p]['display_text'].clear()
        freqs[p]['display_text'].append(freq['display_text'])
        p += 1


def read_file():
    file = open(select_file())
    data = json.load(file)
    file.close()
    update_freqs_display(data)


def write_file():
    file = open(select_file(save=True), "w")
    data = []
    for freq in freqs:
        data.append(
            {
                'memory_bank': freq['memory_bank'].value,
                'memory_channel': freq['memory_channel'].value,
                'memory_pass': freq['memory_pass'].value,
                'receive_frequency': freq['receive_frequency'].value,
                'step_increment': freq['step_increment'].value,
                'receive_mode': freq['receive_mode'].value,
                'attenuator': freq['attenuator'].value,
                'display_text': freq['display_text'].value
            }
        )
    json.dump(data, file, indent=2)
    file.close()


def set_radio():
    pass


def show_read_radio_window():
    read_radio_window.show()


def show_write_radio_window():
    write_radio_window.show()


def read_radio():
    global freqs
    print('Opening serial port', read_port.value)
    ser = serial.Serial(
        read_port.value, read_baud.value, stopbits=serial.STOPBITS_TWO, timeout=timeout)
    ser.write(('MA' + bank.value + '\r').encode())
    p = 0
    while True:
        line = ser.read_until().decode(encoding='ascii')
        new_line = line.replace('\r', '').replace('\n', '')
        print(new_line)
        if len(new_line) > 0:
            freq = decode(new_line)
            if freq is not None:
                freqs[p]['memory_bank'].clear()
                freqs[p]['memory_bank'].append(freq['memory_bank'])
                freqs[p]['memory_channel'].clear()
                freqs[p]['memory_channel'].append(freq['memory_channel'])
                freqs[p]['memory_pass'].clear()
                freqs[p]['memory_pass'].append(freq['memory_pass'])
                freqs[p]['receive_frequency'].clear()
                freqs[p]['receive_frequency'].append(freq['receive_frequency'])
                freqs[p]['step_increment'].clear()
                freqs[p]['step_increment'].append(freq['step_increment'])
                freqs[p]['receive_mode'].clear()
                freqs[p]['receive_mode'].append(freq['receive_mode'])
                freqs[p]['attenuator'].clear()
                freqs[p]['attenuator'].append(freq['attenuator'])
                freqs[p]['display_text'].clear()
                freqs[p]['display_text'].append(freq['display_text'])
                p += 1
        if '\r' not in line:
            break
    ser.close()
    read_radio_window.hide()


def write_radio():
    global freqs
    print('Opening serial port', read_port.value)
    ser = serial.Serial(
        write_port.value, write_baud.value, stopbits=serial.STOPBITS_TWO, timeout=timeout)
    for freq in freqs:
        line = encode(
            {
                'memory_bank': freq['memory_bank'].value,
                'memory_channel': freq['memory_channel'].value,
                'memory_pass': freq['memory_pass'].value,
                'receive_frequency': freq['receive_frequency'].value,
                'step_increment': freq['step_increment'].value,
                'receive_mode': freq['receive_mode'].value,
                'attenuator': freq['attenuator'].value,
                'display_text': freq['display_text'].value
            }
        )
        print(line)
        ser.write((line + '\r').encode(encoding='ascii'))
        ser.readline()
    ser.close()
    write_radio_window.hide()

app = App(layout="grid", title="AR 8000", height=1200, width=800)
app.font = 'Courier'
menubar = MenuBar(app,
                  toplevel=['File', 'Radio'],
                  options=[
                      [
                          ["Open File...", read_file],
                          ["Save As...", write_file]
                      ],
                      [
                          ["Settings", set_radio],
                          ["Read memory bank", show_read_radio_window],
                          ["Write memory", show_write_radio_window]
                      ]
                  ]
                  )

headers = {
    'position': Text(app, text='Pos', grid=[0, 0]),
    'memory_bank': Text(app, text='Bank', grid=[1, 0]),
    'memory_channel': Text(app, text='Channel', grid=[2, 0]),
    'memory_pass': Text(app, text='Pass', grid=[3, 0]),
    'receive_frequency': Text(app, text='Frequency', grid=[4, 0]),
    'step_increment': Text(app, text='Step', grid=[5, 0]),
    'receive_mode': Text(app, text='Mode', grid=[6, 0]),
    'attenuator': Text(app, text='ATT', grid=[7, 0]),
    'display_text': Text(app, text='Display', grid=[8, 0])
}

headers['position'].text_size = 10
headers['memory_bank'].text_size = 10
headers['memory_channel'].text_size = 10
headers['memory_pass'].text_size = 10
headers['receive_frequency'].text_size = 10
headers['step_increment'].text_size = 10
headers['receive_mode'].text_size = 10
headers['attenuator'].text_size = 10
headers['display_text'].text_size = 10

p = 0

for p in range(0, 50):
    freqs.append(
        {
            'position': TextBox(app, width=2, grid=[0, p+1], text=str(p), enabled=False),
            'memory_bank': TextBox(app, width=1, grid=[1, p+1]),
            'memory_channel': TextBox(app, width=2, grid=[2, p+1]),
            'memory_pass': TextBox(app, width=1, grid=[3, p+1]),
            'receive_frequency': TextBox(app, width=10, grid=[4, p+1]),
            'step_increment': TextBox(app, width=6, grid=[5, p+1]),
            'receive_mode': TextBox(app, width=1, grid=[6, p+1]),
            'attenuator': TextBox(app, width=1, grid=[7, p+1]),
            'display_text': TextBox(app, width=7, grid=[8, p+1])
        }
    )
    p += 1

comports = [port[0] for port in serial.tools.list_ports.comports()]

read_radio_window = Window(app, title="Read radio memory bank",
                           width=600, layout="grid", visible=False)
Text(read_radio_window, text="Port", grid=[0, 0], align="left")
read_port = Combo(
    read_radio_window, options=comports, grid=[1, 0], align="left")
Text(read_radio_window, text="Baud rate", grid=[0, 1], align="left")
read_baud = Combo(read_radio_window, options=[
    '2400', '4800', '9600'], selected='9600', grid=[1, 1], align="left")
Text(read_radio_window, text="Memory bank", grid=[0, 2], align="left")
bank = Combo(read_radio_window, options=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                                         'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'],
             grid=[1, 2], align="left")
PushButton(read_radio_window, text='Read', grid=[0, 3], command=read_radio)

write_radio_window = Window(app, title="Write to radio",
                            width=600, layout="grid", visible=False)
Text(write_radio_window, text="Port", grid=[0, 0], align="left")
write_port = Combo(
    write_radio_window, options=comports, grid=[1, 0], align="left")
Text(write_radio_window, text="Baud rate", grid=[0, 1], align="left")
write_baud = Combo(write_radio_window, options=[
    '2400', '4800', '9600'], selected='9600', grid=[1, 1], align="left")
PushButton(write_radio_window, text='Write', grid=[0, 3], command=write_radio)

app.display()
