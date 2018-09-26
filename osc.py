#!/usr/bin/python3
# wykys 2017
# program for download the image screen from TEKTRONIX TDS 320

import time
import os

from uart import UART

IMG_DIR = 'img'


class Oscilocope(object):
    def __init__(self, name=''):
        self.uart = UART(name)

    def send_cmd(self, cmd):
        if type(cmd) == str:
            for c in cmd:
                self.uart.send_byte(ord(c))
            self.uart.send_byte(10)  # LF
            print('Send command {}.'.format(cmd))

    def read_TIFF(self):
        tiff_end = (0x49, 0x46, 0x46, 0x20, 0x44, 0x72, 0x69, 0x76, 0x65, 0x72, 0x20, 0x31, 0x2E, 0x30, 0x00)
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

        if not os.path.exists(IMG_DIR):
            os.makedirs(IMG_DIR)

        img_url = IMG_DIR + '/'
        img_url += time.strftime('%Y-%m-%d_%H-%M-%S_', time.localtime())
        img_url += input('Enter image name >>> ') + '.tiff'

        fw = open(img_url, 'wb')
        fw.write(bytes(img))
        fw.close()
        print('Image created!')


osc = Oscilocope('ATEN USB to Serial Bridge')
osc.read_TIFF()
