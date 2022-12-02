# virtual_simulator

Nothing fancy or complex, just a modbus simulator because company is running out of the real hardware simulator

install:

```shell
pip install git+https://github.com/DAF201/virtual_simulator
```

usage:

```shell
simu [-s --serial default: first COM available] 
     [-t --timeout default:0.15] 
     [-b --baudrate default:115200]
     [-x --xonxoff default: 0]
     [-r --rtscts default: 0]
     [-d --dsrdtr default: 0]
     [-v --visual default: 0]
```

this is debug purpose so it will not auto automatically update data after you manually changed value until a write request is received

![](https://github.com/DAF201/virtual_simulator/blob/main/images/D0EFDD72-7736-4F98-911D-A29A7BC1CAE2.jpg)
![](https://github.com/DAF201/virtual_simulator/blob/main/images/Screenshot%20(126).png)
