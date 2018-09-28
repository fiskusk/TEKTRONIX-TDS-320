from uart import UART

TIFF_END = (
    0x49, 0x46, 0x46, 0x20, 0x44,
    0x72, 0x69, 0x76, 0x65, 0x72,
    0x20, 0x31, 0x2E, 0x30, 0x00
)
TIFF_END_LEN = len(TIFF_END)


class TIFF(object):
    def __init__(self):
        self.data = []
        self.index = 0

    def is_complete(self):
        complate_flag = False
        if self.index > TIFF_END_LEN:
            for index in range(TIFF_END_LEN):
                complate_flag = True
                if (self.data[-1*(index+1)] != TIFF_END[-1*(index+1)]):
                    complate_flag = False
                    break
        return complate_flag

    def append(self, byte):
        self.data.append(byte)
        self.index += 1


def read_tiff(self):
    UART.send_cmd('HARDCopy:PORT RS232')
    UART.send_cmd('HARDCopy:FORMat TIFf')
    UART.send_cmd('HARDCopy:LAYout PORTRait')
    UART.send_cmd('HARDCopy STARt')

    print('Waiting for dates...')

    img = TIFF()
    while not img.is_complete():
        img.append(UART.read_byte())
        print('\rReceive{:71d} B'.format(img.index), end='')

    print('\nReceive Complete')
    return img.data
