import os, sys, io
import M5
from M5 import *
from machine import I2C, Pin, UART
from unit import TOF4MUnit
import time
import json

print("**** AI camera version ****")

# --- 設定値 ---
SCREEN_WIDTH = 640
CENTER_X = SCREEN_WIDTH / 2  # 320 に戻しました
TARGET_R = 30  # ★目標の大きさ（半径）。画像の「r: 20」より少し近づくように設定

# --- グローバル変数 ---
tof4m_0 = None
i2c1 = None
uart_unitv2 = None

def setup():
    global tof4m_0, i2c1, uart_unitv2
    M5.begin()
    
    M5.Display.clear()
    M5.Display.setTextSize(2)
    M5.Display.setTextColor(0xFFFFFF, 0x000000)
    
    i2c1 = I2C(1, scl=Pin(22), sda=Pin(21), freq=100000)
    
    try:
        tof4m_0 = TOF4MUnit(i2c1, 0x29)
        tof4m_0.set_distance_mode(2)
        tof4m_0.set_measurement_timing_budget(500)
        tof4m_0.set_continuous_start_measurement()
    except:
        M5.Display.print("ToF Error")

    uart_unitv2 = UART(2, baudrate=115200, tx=17, rx=16)
    
    M5.Display.print("AI & ToF System Start")
    time.sleep(1)
    M5.Display.clear()

def turn_inplace(speed, direction="right"):
    """
    超信地旋回（その場で回転）
    speed: 0 ~ 100
    direction: "right" (時計回り) / "left" (反時計回り)
    """
    if direction == "right":
        # zにプラスの値を入れると右回転（車体によりますが一般的）
        send_motor(0, 0, speed)
    elif direction == "left":
        # zにマイナスの値を入れると左回転
        send_motor(0, 0, speed)
    else:
        send_motor(0, 0, 0)

def send_motor(x, y, z):
    global i2c1  
    try:
        vx = max(min(int(x), 100), -100)
        vy = max(min(int(y), 100), -100)
        wz = max(min(int(z), 100), -100)
        
        b = (vx & 0xFFFF).to_bytes(2, 'little') + \
            (vy & 0xFFFF).to_bytes(2, 'little') + \
            (wz & 0xFFFF).to_bytes(2, 'little')
            
        i2c1.writeto(0x08, b)
    except:
        pass

def run_ai_tracking():
    global uart_unitv2
    
    print("--- AIモードの処理まできています！ ---")
    
    latest_data = None
    read_count = 0
    while uart_unitv2.any() and read_count < 10:
        try:
            line = uart_unitv2.readline()
            
            # ★★★ ここに1行追加！カメラからの生データをパソコンに表示します ★★★
            print("受信:", line) 
            
            if line:
                line_str = line.decode('utf-8').strip()
                if line_str.startswith('{') and line_str.endswith('}'):
                    data = json.loads(line_str)
                    if 'cx' in data and 'r' in data:
                        latest_data = data
        except Exception as e:
            print("エラー:", e) # エラーがあったら表示
        read_count += 1
            
    # （これ以降のコードはそのまま）
            
    # 最新の認識データが見つかった場合
    if latest_data:
        obj_x = latest_data['cx']
        obj_r = latest_data['r']
        
        # 1. 旋回制御（画面の端にあるものを追いかける）
        diff_x = obj_x - CENTER_X
        turn_speed = int(diff_x * 0.15)
        
        # 画面の中央付近にいるときはフラフラしないように旋回ストップ
        if abs(diff_x) < 60:
            turn_speed = 0
        else:
            # 端の方にいるとき、パワーが弱すぎてモーターが回らないのを防ぐ
            if turn_speed > 0 and turn_speed < 25: turn_speed = 25
            if turn_speed < 0 and turn_speed > -25: turn_speed = -25
            
        # 2. 前後制御（半径の大きさで距離を保つ）
#         forward_speed = 0
#         if obj_r < TARGET_R - 5: # rが小さい(遠い) → 前進
#             forward_speed = 40
#         elif obj_r > TARGET_R + 10: # rが大きい(近すぎる) → 後退
#             forward_speed = -20
            
        # PCの画面で実際のスピードを確認できます
        print("AI Tracking -> FWD:", 0, " TRN:", turn_speed, " (X:", obj_x, " R:", obj_r, ")")
        
        # モーター送信
        #send_motor(forward_speed, 0, turn_speed)
        if turn_speed == 0:
            send_motor(30, 0, 0)
        elif turn_speed > 0:
            turn_inplace(turn_speed, "right")
        elif turn_speed < 0:
            turn_inplace(turn_speed, "left")
        
        M5.Display.setCursor(160, 100)
        M5.Display.print("AI: Tracking... ")
        return
    
    # データがない場合
    send_motor(0, 0, 0)
    M5.Display.setCursor(160, 100)
    M5.Display.print("AI: Searching...  ")


def loop():
    global tof4m_0
    M5.update()
    
    distance = 0
    if tof4m_0.get_data_ready:
        distance = tof4m_0.get_distance
        if distance is None: return

        M5.Display.setCursor(10, 20)
        M5.Display.print("Dist: " + str(distance) + " mm    ")
        M5.Display.setCursor(10, 60)

        if distance <= 50:
            M5.Display.setTextColor(0xFF0000, 0x000000)
            M5.Display.print("STOP !!!        ")
            M5.Display.setTextColor(0xFFFFFF, 0x000000)
            send_motor(0, 0, 0)
        elif distance <= 200:
            M5.Display.print("Avoid!          ") 
            send_motor(0, 0, 50) 
        elif distance <= 700:
            M5.Display.print("Slow Down       ")
            send_motor(50, 0, 0)
        elif distance > 700:
            M5.Display.print("AI Tracking Mode")
            run_ai_tracking()

    time.sleep(0.1)

if __name__ == '__main__':
    setup()
    while True:
        loop()
