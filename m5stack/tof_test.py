import os, sys, io
import M5
from M5 import *
from machine import I2C, Pin
from unit import TOF4MUnit  # ユニット用ライブラリ
import time

tof4m_0 = None

def setup():
    global tof4m_0
    M5.begin()
    
    i2c1 = I2C(1, scl=Pin(22), sda=Pin(21), freq=100000)
    print("i2c1.scan=", i2c1.scan())
    
    tof4m_0 = TOF4MUnit(i2c1, 0x29)
    tof4m_0.set_distance_mode(2)
    tof4m_0.set_measurement_timing_budget(500)
    tof4m_0.set_continuous_start_measurement()
    
def loop():
    global tof4m_0
    M5.update()
    if tof4m_0.get_data_ready:
        print(str((str("Distance:") + str((str(tof4m_0.get_distance) + str("mm"))))))
    time.sleep(0.1)

if __name__ == '__main__':
    setup()
    while True:
        loop()