from src import modbus, UI

if __name__ == '__main__':
    modbus_obj = modbus.modbus_serial()
    modbus_obj.run()
