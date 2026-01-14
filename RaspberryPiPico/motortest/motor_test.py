from m5stack import *
from m5ui import *
from uiflow import *
import i2c_bus

setScreenColor(0x111111)

x = 0
y = 0
z = 0

b = int(x).to_bytes(2, 'little') + int(y).to_bytes(2, 'little') + int(z).to_bytes(2, 'little')

i2c0 = i2c_bus.easyI2C(i2c_bus.PORTA, 0x00, freq=100000)
i2c0.addr=(0x08)

print(i2c0.scan())

i2c0.write_mem_list(0, b)
