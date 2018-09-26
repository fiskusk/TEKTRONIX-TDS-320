#!/usr/bin/python3
# wykys 2017
# program for download the image screen from TEKTRONIX TDS 320

import serial
import time
import sys
import os
import csv

DATA_DIR = 'fchar_data'

class OsciloImageReader():
    def __init__(self, port):
        """ initialization """
        self.port = port
        self.ser = serial.Serial()
        self.open_serial_port()
        self.send_commands()
        self.recieve_values()

    def open_serial_port(self):
        """ open connection """
        
        self.ser.port = self.port
        self.ser.baudrate = 19200
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.parity = serial.PARITY_NONE
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.timeout = None
        try:
            self.ser.open()
            print('Port {} is open.'.format(self.port))
        except serial.SerialException:
            print('Port {} opening error!'.format(self.port))
            sys.exit()

    def read_byte(self):
        """ read one byte """
        return int.from_bytes(self.ser.read(1), byteorder='little', signed=False)

    def send_byte(self, byte):
        """ write one byte """
        self.ser.write(bytes((byte,)))
        time.sleep(0.01)

    def send_cmd(self, cmd):
        """ send command """
        if type(cmd) == str:
            for c in cmd:
                self.send_byte(ord(c))
            self.send_byte(10) # LF
            print('Send command {}.'.format(cmd))

    def close_serial_port(self):
        """ end connection """
        self.ser.close()
        print('Close port')

    def read_value(self,data_url):
        read_complete = False

        value = []

        while (not read_complete):
            byte = self.read_byte()
            value.append(byte)

            # check end read
            if (byte == 10):
                read_complete = True
        s = "".join(chr(i) for i in value)
        print('\nRead value is ', s)

        with open(data_url,"a") as f:
            writer = csv.writer(f,delimiter=";")
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
        data = []
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

        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        
        self.close_serial_port()

if sys.platform == 'win32':
    OsciloImageReader('COM12')
else:
    OsciloImageReader('/dev/ttyUSB0')
