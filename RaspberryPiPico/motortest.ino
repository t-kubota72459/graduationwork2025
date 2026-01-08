#include <Wire.h>
#include <Arduino.h>
#include <math.h>

#include "Motor.h"
#include "Mecanum.h"

// --- I2C設定 ---
#define I2C_SLAVE_ADDRESS   0x08
#define SDA_PIN             16
#define SCL_PIN             17

// --- M5Stackから受信するデータ構造の定義 ---
// Vx, Vy, Wzを short (2bytes) 合計 6 bytes で受け取る。
struct CommandData {
  int16_t Vx;       // 前後方向の速度 (-100 to 100)
  int16_t Vy;       // 左右方向の速度 (-100 to 100)
  int16_t Wz;       // 旋回方向の速度 (-100 to 100)
};

CommandData currentCommand = {0, 0, 0}; // 受信データを格納する変数

// --- モーター制御クラスのインスタンス ---M
//           en を PWM 制御する
//           in1 と in2 の組み合わせで正転・逆転制御
//           en, in1, in2 
Motor motorFL(6, 7, 8, true); 
Motor motorFR(9, 10, 11, true); 
Motor motorRL(12, 13, 14);
Motor motorRR(18, 19, 20);

Mecanum mecanum(motorFL, motorFR, motorRL, motorRR);

// I2Cデータ受信時に呼び出される関数
void receiveEvent(int byteCount) {
  // 受信データが期待するサイズと異なる場合は無視
  const int expectedBytes = sizeof(CommandData);
  if (byteCount != expectedBytes) {
    // データエラーの通知など
    while (Wire.available()) Wire.read(); // バッファをクリア
    return;
  }
  Wire.readBytes((byte*)&currentCommand, sizeof(CommandData));
}

void setup() {
  Serial.begin(115200);
  Serial.println("Pico I2C Slave Mode Started.");

  // I2C通信の初期化 (スレーブモード)
  Wire.setSDA(SDA_PIN);
  Wire.setSCL(SCL_PIN);
  Wire.begin(I2C_SLAVE_ADDRESS);
  
  // 受信イベントハンドラを登録
  Wire.onReceive(receiveEvent);

  mecanum.setup();
}

void loop() {
  mecanum.drive(currentCommand.Vx, currentCommand.Vy, currentCommand.Wz);
  delay(50); // M5Stackからの指令を待機
}
