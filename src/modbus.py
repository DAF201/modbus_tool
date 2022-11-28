import serial
import serial.tools.list_ports
import threading
import gc
import re
import json
AVAILABLE_SERIAL_PORTS = [x.device
                          for x in serial.tools.list_ports.comports()]


class modbus_serial(serial.Serial):
    def __init__(self, serial_port: str, HEX=False, *args, **kwargs) -> None:
        self.serial_port: str
        self.timeout: float
        self.baudrate: int
        self.xonxoff: bool
        self.rtscts: bool
        self.dsrdtr: bool
        self.HEX = bool
        self.reading_thread: threading.Thread
        self.writing_thread: threading.Thread
        self.recving_buffer: bytes
        self.modbus_message_pool: list
        self.data_base: dict

        super().__init__(serial_port, *args, **kwargs)

        self.serial_port = serial_port
        self.HEX = HEX
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
        while (1):
            self.recving_buffer = self.read(128)
            if self.recving_buffer != b'':
                hex_data = self.recving_buffer.hex()
                if self.HEX:
                    print(' '.join(re.findall('..', hex_data)))
                else:
                    print(self.recving_buffer)
                self.modbus_message_pool.append(
                    (hex_data[:2], hex_data[2:4], hex_data[4:-4], hex_data[-4:]))
                self.recving_buffer = b''

    def __execute(self):
        while (1):
            try:
                if len(self.modbus_message_pool) == 0:
                    continue
                message = self.modbus_message_pool[0]
                host = message[0]
                function_code = message[1]
                data = message[2]
                crc = message[3]

                if function_code == '03':
                    target_register_address = int(data[:4], 16)
                    number_of_registers = int(data[4:], 16)
                    ret = []
                    for x in range(number_of_registers):
                        ret.append(
                            self.data_base[str(target_register_address+x)])
                    self.write(b'')
                    print(ret)
            except Exception as e:
                print(e)
            finally:
                if len(self.modbus_message_pool) != 0:
                    self.modbus_message_pool.pop(0)

    def stop(self):
        self.is_running = False

    def __del__(self) -> None:
        gc.collect()

    def __str__(self) -> str:
        return ("""serial: %s\ntime out: %f\nbaudrate: %d\nxonxoff: %d\nrtscts: %d\ndsrdtr: %d\nHEX display: %d""" % (self.serial_port, self.timeout, self.baudrate, self.xonxoff, self.rtscts, self.dsrdtr, self.HEX))


modbus_obj = modbus_serial(AVAILABLE_SERIAL_PORTS[0], HEX=True, timeout=0.15,
                           baudrate=115200, xonxoff=False, rtscts=False, dsrdtr=False)
print(modbus_obj)
modbus_obj.run()
