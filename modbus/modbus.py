import serial
import serial.tools.list_ports
import threading
import gc
import json
import sys
import os
import argparse

AVAILABLE_SERIAL_PORTS = [x.device
                          for x in serial.tools.list_ports.comports()]

VIRTUAL_DB = {}
try:
    with open('db.json', 'r')as json_db:
        VIRTUAL_DB = json.load(json_db)
except:
    temp = {}
    for x in range(40000, 50000):
        temp[x] = '0000'

    with open('db.json', 'w')as db_json:
        json.dump(temp, db_json)

    with open('db.json', 'r')as json_db:
        VIRTUAL_DB = json.load(json_db)


class MODBUS(serial.Serial):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__receive_message_thread: threading.Thread
        self.__response_message_thread: threading.Thread
        self.message_pool: list
        self.message_pool = []
        self.ALIVE = True

    def start(self):
        self.__receive_message_thread = threading.Thread(
            target=self.__receive_message)
        self.__response_message_thread = threading.Thread(
            target=self.__response_message)

        self.__receive_message_thread.daemon = True
        self.__response_message_thread.daemon = True

        self.__receive_message_thread.start()
        self.__response_message_thread.start()
        while (self.ALIVE):
            pass

    def stop(self):
        self.ALIVE = False
        return self.ALIVE

    def __receive_message(self):
        while (1):
            try:
                receive_buffer = self.read(128)

                if receive_buffer == b'':
                    continue
                hex_data = receive_buffer.hex()

                if not self.__modbus_CRC_check(hex_data):
                    continue

                print('recv:', hex_data)

                self.message_pool.append([hex_data[:2], hex_data[2:4],
                                          hex_data[4:8], hex_data[8:-4]])

            except Exception as general_exception:
                print(general_exception)
            finally:
                gc.collect()

    def __response_message(self):
        while (1):
            try:
                if len(self.message_pool) == 0:
                    continue

                message = self.message_pool.pop(0)

                if message[1] == '03':
                    response = self.__modbus_response_formator(message)
                    self.write(bytes.fromhex(response))
                    continue

                if message[1] == '10':

                    data = []
                    for x, y in zip(*[iter(self.data_split(message[3][6:], size=2, hex=False))]*2):
                        data.append(x+y)

                    for x in range(int(message[3][:4], 16)):
                        VIRTUAL_DB[str(int(message[2], 16)+x)] = data[x]
                    with open('db.json', 'w')as json_db:
                        json.dump(VIRTUAL_DB, json_db)

            except Exception as general_exception:
                print(general_exception)
            finally:
                gc.collect()

    def __modbus_response_formator(self, message: list):
        ret = message[0]+message[1]+hex(2*int(message[3], 16))[2:].zfill(2)
        for x in range(int(message[3], 16)):
            ret += VIRTUAL_DB[str(int(message[2], 16)+x)]
        ret += self.__modbus_CRC_calculate(ret)
        return ret

    def data_split(self, data: str, size=2, hex=True) -> list:
        if hex:
            return [int(data[x-size:x], 16) for x in range(size, len(data)+size, size)]
        else:
            return [data[x-size:x] for x in range(size, len(data)+size, size)]

    def __modbus_CRC_calculate(self, data: str) -> str:

        crc = 0xffff
        A001H = 0xA001
        data = self.data_split(data)

        for x in data:
            crc = crc ^ x
            for i in range(0, 8):
                if bin(crc)[-1:] == '1':
                    crc = crc >> 1
                    crc = crc ^ A001H
                else:
                    crc = crc >> 1

        res = hex((crc >> 8) | (crc << 8))
        return (res[int(len(res)/2):])

    def __modbus_CRC_check(self, data: str) -> str:
        return self.__modbus_CRC_calculate(data[:-4]) == data[-4:]

    def __del__(self) -> None:
        gc.collect()
        return super().__del__()


def main():
    argparser = argparse.ArgumentParser()

    argparser.add_argument('-s', '--serial', type=str,
                           default=AVAILABLE_SERIAL_PORTS[0])
    argparser.add_argument('-t', '--timeout', type=float, default=0.15)
    argparser.add_argument('-b', '--baudrate', type=int, default=115200)
    argparser.add_argument('-x', '--xonxoff', type=int, default=0)
    argparser.add_argument('-r', '--rtscts', type=int, default=0)
    argparser.add_argument('-d', '--dsrdtr', type=int, default=0)
    argparser.add_argument('-v', '--visual', action='store_true')
    
    args = argparser.parse_args()

    if not args.visual:
        sys.stdout = open(os.devnull, 'w')

    simulator = MODBUS(args.serial, timeout=args.timeout,
                       baudrate=args.baudrate, xonxoff=args.xonxoff, rtscts=args.rtscts, dsrdtr=args.dsrdtr)
    simulator.start()
