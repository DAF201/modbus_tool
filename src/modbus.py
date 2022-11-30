import serial
import serial.tools.list_ports
import threading
import gc
import re
import json
AVAILABLE_SERIAL_PORTS = [x.device
                          for x in serial.tools.list_ports.comports()]


class modbus_serial(serial.Serial):
    def __init__(self, serial_port: str, *args, **kwargs) -> None:
        self.serial_port: str
        self.timeout: float
        self.baudrate: int
        self.xonxoff: bool
        self.rtscts: bool
        self.dsrdtr: bool
        self.reading_thread: threading.Thread
        self.writing_thread: threading.Thread
        self.recving_buffer: bytes
        self.modbus_message_pool: list
        self.data_base: dict

        super().__init__(serial_port, *args, **kwargs)

        self.serial_port = serial_port
        self.is_running = False
        self.recving_buffer = ''
        self.modbus_message_pool = []
        with open('db.json', 'r')as db:
            self.data_base = json.load(db)

    def run(self) -> None:
        self.reading_thread = threading.Thread(target=self.__recv)
        self.reading_thread.daemon = True
        self.writing_thread = threading.Thread(target=self.__execute)
        self.writing_thread.daemon = True
        self.reading_thread.start()
        self.writing_thread.start()
        self.is_running = True
        while (self.is_running):
            pass

    def __recv(self):
        self.__last_recv_register = ''
        while (1):
            try:
                self.recving_buffer = self.read(128)
                # print(self.recving_buffer)
                hex_data = self.recving_buffer.hex()
                if hex_data != '':
                    print(hex_data)
                if hex_data[4:8] == self.__last_recv_register:
                    continue
                if self.recving_buffer != b'':
                    if not self.__modbus_check(hex_data[:-4], hex_data[-4:]):
                        self.recving_buffer = b''
                        continue
                    else:
                        self.modbus_message_pool.append(
                            {'host_address': hex_data[:2], 'function_type': hex_data[2:4],
                             'register_address': hex_data[4:8], 'number_of_register': hex_data[8:-4]})
                        self.__last_recv_register = hex_data[4:8]
                    self.recving_buffer = b''
            except Exception as e:
                print(e)
                pass

    def __execute(self):
        while (1):
            try:
                if len(self.modbus_message_pool) == 0:
                    continue
                modbus_message = self.modbus_message_pool[0]
                self.modbus_message_pool.pop(0)
                if modbus_message['function_type'] == '03':
                    print('reading', modbus_message['register_address'])
                    ret = modbus_message['host_address'] + \
                        modbus_message['function_type'] + \
                        hex(2*int(
                            modbus_message['number_of_register'], 16))[2:].zfill(2)
                    for x in range(2*int(modbus_message['number_of_register'], 16)):
                        ret += self.data_base[str(
                            int(modbus_message['register_address'], 16)+x-1)]
                    ret += self.__modbus_calculate(ret)
                    ret = bytes.fromhex(ret)
                    self.write(ret)
                    print(ret.hex())
                if modbus_message['function_type'] == '10':
                    pass
            except Exception as e:
                print(e)
                pass

    @classmethod
    def __modbus_check(self, data: str, crc_data: str) -> str:
        return self.__modbus_calculate(data) == crc_data

    @classmethod
    def __modbus_calculate(self, data: str) -> str:
        def modbus_data_split(data: str, size=2) -> list:
            return [int(data[x-size:x], 16) for x in range(size, len(data)+size, size)]
        crc = 0xffff
        A001H = 0xA001
        data = modbus_data_split(data)
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

    def stop(self):
        self.is_running = False

    def __del__(self) -> None:
        gc.collect()

    def __str__(self) -> str:
        return ("""serial: %s\ntime out: %f\nbaudrate: %d\nxonxoff: %d\nrtscts: %d\ndsrdtr: %d\n""" % (self.serial_port, self.timeout, self.baudrate, self.xonxoff, self.rtscts, self.dsrdtr))


modbus_obj = modbus_serial(AVAILABLE_SERIAL_PORTS[0], timeout=0.15,
                           baudrate=115200, xonxoff=False, rtscts=False, dsrdtr=False)
print(modbus_obj)
modbus_obj.run()
