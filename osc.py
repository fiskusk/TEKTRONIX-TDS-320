#!/usr/bin/python3
# wykys 2017
# program for download the image screen from TEKTRONIX TDS 320

import time
import os
import csv

from uart import UART

IMG_DIR = 'img'
DATA_DIR = 'fchar_data'


def check_dir(name=''):
    if not os.path.exists(name):
        os.makedirs(name)


class Oscilocope(object):
    def __init__(self, name=''):
        self.uart = UART(name, baudrate=19200)

    def send_cmd(self, cmd):
        if type(cmd) == str:
            for c in cmd:
                self.uart.send_byte(ord(c))
            self.uart.send_byte(10)  # LF
            print('Send command {}.'.format(cmd))

    def read_tiff(self):
        tiff_end = (
            0x49, 0x46, 0x46, 0x20, 0x44,
            0x72, 0x69, 0x76, 0x65, 0x72,
            0x20, 0x31, 0x2E, 0x30, 0x00
        )
        tiff_end_len = len(tiff_end)
        image_complate = False

        img = []
        i = 0

        self.send_cmd('HARDCopy:PORT RS232')
        self.send_cmd('HARDCopy:FORMat TIFf')
        self.send_cmd('HARDCopy:LAYout PORTRait')
        self.send_cmd('HARDCopy STARt')

        print('Waiting for dates...')

        while (not image_complate):
            byte = self.uart.read_byte()
            img.append(byte)
            i += 1

            print('\rReceive{:71d} B'.format(i), end='')

            # check end file
            if (byte == 0 and i > tiff_end_len):
                for j in range(tiff_end_len):
                    image_complate = True
                    if (img[-1*(j+1)] != tiff_end[-1*(j+1)]):
                        image_complate = False
                        break

        print('\nReceive Complete')

        check_dir(IMG_DIR)

        img_url = IMG_DIR + '/'
        img_url += time.strftime('%Y-%m-%d_%H-%M-%S_', time.localtime())
        img_url += input('Enter image name >>> ') + '.tiff'

        fw = open(img_url, 'wb')
        fw.write(bytes(img))
        fw.close()
        print('Image created!')

    def read_value(self, data_url):
        read_complete = False

        value = []

        while (not read_complete):
            byte = self.read_byte()
            value.append(byte)

            # check end read
            if (byte == 10):
                read_complete = True
        s = ''.join(chr(i) for i in value)
        print('\nRead value is ', s)

        with open(data_url, "a") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([s])

    def send_commands(self):
        self.send_byte(3)
        self.send_cmd('SELECT:CH1 ON')
        self.send_cmd('SELECT:CH2 ON')
        self.send_cmd('CH1:SCAle 2')
        self.send_cmd('CH2:SCAle 2')
        self.send_cmd('CH1:POSition 0')
        self.send_cmd('CH2:POSition 0')

        self.send_cmd('MEASUrement:MEAS1:SOUrce1 CH1')
        self.send_cmd('MEASUrement:MEAS1:TYPE RMS')
        self.send_cmd('MEASUrement:MEAS1:STATE ON')

        self.send_cmd('MEASUrement:MEAS2:SOUrce1 CH2')
        self.send_cmd('MEASUrement:MEAS2:TYPE RMS')
        self.send_cmd('MEASUrement:MEAS2:STATE ON')

        self.send_cmd('MEASUrement:MEAS3:SOUrce1 CH1')
        self.send_cmd('MEASUrement:MEAS3:TYPE FREQuency')
        self.send_cmd('MEASUrement:MEAS3:STATE ON')

        print('Commands sended')

    def recieve_values(self):
        data_url = DATA_DIR + '/'
        data_url += time.strftime('%Y-%m-%d_%H-%M-%S_', time.localtime())
        data_url += input('Enter image name >>> ') + '.csv'

        self.send_cmd('MEASUrement:MEAS1:VALue?')
        self.read_value(data_url)

        self.send_cmd('MEASUrement:MEAS2:VALue?')
        self.read_value(data_url)

        self.send_cmd('MEASUrement:MEAS3:VALue?')
        self.read_value(data_url)

        key = input("For stop write everything except 0: ")
        while (key == ' '):
            self.send_cmd('MEASUrement:MEAS1:VALue?')
            self.read_value(data_url)

            self.send_cmd('MEASUrement:MEAS2:VALue?')
            self.read_value(data_url)

            self.send_cmd('MEASUrement:MEAS3:VALue?')
            self.read_value(data_url)

            key = input("For stop write everything except 0: ")

        check_dir(DATA_DIR)


osc = Oscilocope('ATEN USB to Serial Bridge')
osc.read_tiff()
osc.send_commands()
osc.recieve_values()
