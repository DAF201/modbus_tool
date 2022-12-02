def __modbus_CRC_check(data: str) -> str:
    def data_split(data: str, size=2) -> list:
        return [int(data[x-size:x], 16) for x in range(size, len(data)+size, size)]

    def __modbus_CRC_calculate(data: str) -> str:
        crc = 0xffff
        A001H = 0xA001
        data = data_split(data)

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

    return __modbus_CRC_calculate(data[:-4]) == data[-4:]


print(__modbus_CRC_check('01039c8f00045bb2'))
