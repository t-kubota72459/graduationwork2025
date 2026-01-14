import M5
from M5 import *
from machine import I2C, Pin
from unit import TOF4MUnit
import time
import struct

# --- 設定項目 ---
PICO_ADDR = 0x08				# Raspi PicoのI2Cアドレス
DISTANCE_THRESHOLD = 200		# 停止する距離 (mm)
SAFE_DISTANCE = 400			# 前進を再開する距離 (mm)
NORMAL_SPEED = 30			# 通常時の前進速度
TURN_SPEED = 30				# 回避時の旋回速度

# --- グローバル変数 ---
tof = None
i2c_bus = None

def setup():
    """
    セットアップ関数
    """
    global tof, i2c_bus
    M5.begin()
    
    M5.Lcd.clear()
    M5.Lcd.setTextSize(2)
    M5.Lcd.setCursor(0, 0)
    M5.Lcd.print("Robot Status" + "\n")
    M5.Lcd.print("------------" + "\n")
    
    i2c_bus = I2C(1, scl=Pin(22), sda=Pin(21), freq=100000)
    print("I2C Devices found:", i2c_bus.scan())
    
    tof = TOF4MUnit(i2c_bus, 0x29)
    tof.set_distance_mode(2) 
    tof.set_measurement_timing_budget(500)
    tof.set_continuous_start_measurement()
    
    print("System Ready!")

def send_motor_command(x, y, z):
    """Picoに走行指示を送る関数"""
    try:
        # int16 (short) 3つ分を little-endian でバイナリ化
        data = struct.pack('<hhh', int(x), int(y), int(z))
        i2c_bus.writeto(PICO_ADDR, data)
    except Exception as e:
        pass
        # print("I2C Send Error:", e)

def display_status(dist_str, behavior_str, color):
    """画面をコクピット風にデザイン (printlnを使わない版)"""
    
    # --- 1. 描画エリアのクリア ---
    # 毎回全体を clear するとチラつくので、動く部分だけ塗りつぶす
    M5.Lcd.fillRect(0, 40, 320, 200, 0x000000) 
    
    # --- 2. 距離の表示 (大きく表示) ---
    M5.Lcd.setTextSize(2)
    M5.Lcd.setCursor(20, 50)
    M5.Lcd.setTextColor(0xFFFFFF) # 白
    M5.Lcd.print("RANGE:")
    
    M5.Lcd.setCursor(110, 45)
    M5.Lcd.setTextSize(4)         # 数字を強調
    M5.Lcd.print(dist_str)
    
    # --- 3. 視覚的なバー表示 (インジケーター) ---
    # 文字列 "123mm" から数値 123 を取り出す
    try:
        d_val = int(dist_str.replace('mm', ''))
        # 300mmを100%としてバーの長さを計算 (最大280ピクセル)
        bar_width = int(min(d_val, 300) / 300 * 280)
        
        # バーの枠線を描く
        M5.Lcd.drawRect(20, 95, 280, 25, 0x555555)
        # 距離に応じた色のバーを描く
        M5.Lcd.fillRect(20, 95, bar_width, 25, color)
    except:
        # None の場合などはバーを描画しない
        pass

    # --- 4. 挙動の表示 ---
    M5.Lcd.setTextSize(2)
    M5.Lcd.setCursor(20, 140)
    M5.Lcd.setTextColor(0x00AAFF) # 水色
    M5.Lcd.print("SYSTEM STATE:")
    
    M5.Lcd.setCursor(40, 180)
    M5.Lcd.setTextSize(3)
    M5.Lcd.setTextColor(color)
    M5.Lcd.print(">> " + behavior_str)
    
def loop():
    M5.update()
    
    if tof.get_data_ready:
        distance = tof.get_distance
        
        if distance is None:
            display_status("Out of Range", "STOP (Safe)", 0xFFAA00)
            send_motor_command(0, 0, 0)
            return
        
        if distance < DISTANCE_THRESHOLD:
            display_status(str(distance)+"mm", "TURNING", 0xFF0000)
            send_motor_command(0, 0, TURN_SPEED) 
        elif distance < SAFE_DISTANCE:
            display_status(str(distance)+"mm", "SLOWDOWN", 0xFF0000)
            send_motor_command(15, 0, 0)
        else:
            display_status(str(distance)+"mm", "FORWARD", 0x00FF00)
            send_motor_command(NORMAL_SPEED, 0, 0)
    
    time.sleep(0.1)

if __name__ == '__main__':
    setup()
    while True:
        loop()