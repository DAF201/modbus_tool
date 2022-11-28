import serial
import serial.tools.list_ports
import threading
from time import time, sleep
import json
AVAILABLE_SERIAL_PORTS = [x.device
                          for x in serial.tools.list_ports.comports()]


def update_available_serial_ports():
    global AVAILABLE_SERIAL_PORTS
    AVAILABLE_SERIAL_PORTS = [x.device
                              for x in serial.tools.list_ports.comports()]


class serial_port(serial.Serial):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.buffer = ''
        self.last_recieved_char = ''
        self.last_read_time = 0
        self.last_buffer_size = 0
        self.last_buffer_splited = False

        self.command_pool = []

        self.serial_read_thread = threading.Thread(target=self.serial_read)
        self.serial_read_thread.daemon = True
        self.serial_timer_thread = threading.Thread(target=self.serial_timer)
        self.serial_timer_thread.daemon = True

        self.serial_read_thread.start()
        self.serial_timer_thread.start()

    def serial_timer(self):
        while (1):
            if self.last_recieved_char != '\n':
                self.last_recieved_char = '\n'

                if self.buffer != '':
                    buffer_size = len(self.buffer)
                    if buffer_size < 8:
                        continue
                    if (self.last_buffer_splited and buffer_size == self.last_buffer_size) or (buffer_size > self.last_buffer_size and buffer_size/2 == self.last_buffer_size):
                        self.command_pool.append(self.buffer[:buffer_size//2])
                        self.command_pool.append(self.buffer[buffer_size//2:])
                        self.last_buffer_splited = True
                    else:
                        self.command_pool.append(self.buffer)
                        self.last_buffer_splited = False

                    self.last_buffer_size = buffer_size
                    self.buffer = ''

    def serial_read(self):
        while (1):
            serial_buffer = self.read(128)
            self.buffer = self.buffer+str(serial_buffer.hex())
            self.last_read_time = time()
            self.last_recieved_char = serial_buffer

    def serial_write(self, data):
        self.write(data)

    def __del__(self) -> None:
        return super().__del__()


class modbus_serial_port(serial_port):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            with open('simulator.json', 'r')as file_storage:
                self.data_buffer = json.load(file_storage)
        except Exception as e:
            print(e)
            self.data_buffer = {}
        self.command_fetching_and_execution_thread = threading.Thread(
            target=self.command_fetching)
        self.command_fetching_and_execution_thread.daemon = True

        self.file_update_thread = threading.Thread(
            target=self.file_update, args=(5,))

        self.command_fetching_and_execution_thread.start()
        self.file_update_thread.start()

    def file_update(self, time_interval):
        while (1):
            with open('simulator.json', 'w')as file_storage:
                json.dump(self.data_buffer, file_storage)
            sleep(time_interval)

    def command_fetching(self):
        while (1):
            if len(self.command_pool) != 0:
                self.command_execution()

    def command_execution(self):
        command = self.command_pool[0]
        address = command[:2]
        command_type = command[2:4]
        register_address = command[4:8]
        number_of_registers = command[8:12]
        if command_type == '06':
            data = command[8:16]
        crc = command[-4:]
        if command_type == '06' and all(map(lambda x: x != '', (address, command_type, register_address, data, crc))):
            print('writing:', register_address,
                  'number of registers:', number_of_registers, 'data:', data)
            self.data_buffer[register_address] = data
            print(self.command_pool[0])
        else:
            try:
                print('reading:', register_address,
                      'number of registers:', number_of_registers, 'value:', self.data_buffer[register_address])
            except:
                pass
        self.command_pool.pop(0)


modbus = modbus_serial_port(AVAILABLE_SERIAL_PORTS[0], timeout=0.15,
                            baudrate=19200, xonxoff=False, rtscts=False, dsrdtr=False)
