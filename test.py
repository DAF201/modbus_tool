# import json

# import random

# data = {}
# for x in range(40000, 40300):
#     data[x] = hex(random.randrange(0, 127))[2:].rjust(2, '0')
# with open('db.json', 'w')as js:
#     json.dump(data, js)
import crc16

# print(crc16.crc16xmodem(b'01039c730005'))
import crc16
print(crc16.crc16xmodem(b'123456789'))
