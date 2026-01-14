from machine import I2C, Pin
import time

i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=100000)
print("i2c1.scan=", i2c.scan())

x = 0
y = 0
z = 30
b = int(x).to_bytes(2, 'little') + int(y).to_bytes(2, 'little') + int(z).to_bytes(2, 'little')

i2c = i2c.writeto(0x08, b)