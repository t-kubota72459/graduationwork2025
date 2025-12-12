#include <Wire.h>
#include <Arduino.h>
#include <math.h>

#include "Motor.h"

// --- I2C設定 ---
#define I2C_SLAVE_ADDRESS   0x08
#define SDA_PIN             16
#define SCL_PIN             17

// --- M5Stackから受信するデータ構造の定義 ---
// Vx, Vy, Wzをfloat型（4バイト）で受け取ります。
struct CommandData {
  int16_t Vx;       // 前後方向の速度 (-1.0 to 1.0)
  int16_t Vy;       // 左右方向の速度 (-1.0 to 1.0)
  int16_t Wz;       // 旋回方向の速度 (-1.0 to 1.0)
};

CommandData currentCommand = {0, 0, 0}; // 受信データを格納する変数

// --- モーター制御クラスのインスタンス ---
Motor motorFL(6, 7, 8); 
Motor motorFR(9, 10, 11); 
Motor motorRL(12, 13, 14);
Motor motorRR(18, 19, 20);

// I2Cデータ受信時に呼び出される関数
void receiveEvent(int byteCount) {
  // 受信データが期待するサイズと異なる場合は無視
  const int expectedBytes = sizeof(CommandData) + 1;
  if (byteCount != expectedBytes) {
    // データエラーの通知など
    while (Wire.available()) Wire.read(); // バッファをクリア
    return;
  }
  
  Wire.read();
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

  motorFL.setup();
  motorFR.setup();
}

void loop() {
  // 受信した最新のコマンドをシリアルモニタに出力 (デバッグ用)
  float fVx = (float)currentCommand.Vx / 100.0f;
  float fVy = (float)currentCommand.Vy / 100.0f;
  float fWz = (float)currentCommand.Wz / 100.0f;

  Serial.print("fVx: "); Serial.print(fVx);
  Serial.print(" | fVy: "); Serial.print(fVy);
  Serial.print(" | fWz: "); Serial.println(fWz);

  motorFL.setSpeed(abs(int(fVx*255.0f)), fVx > 0);
  motorFR.setSpeed(abs(int(fVx*255.0f)), fVx > 0);

  motorRL.setSpeed(abs(int(fVx*255.0f)), fVx > 0);
  motorRR.setSpeed(abs(int(fVx*255.0f)), fVx > 0);

  // --- モーター制御の実行 ---
  // car.move(currentCommand.Vx, currentCommand.Vy, currentCommand.Wz);
  // car.move の中では、Vx, Vy, Wzの値を使って4輪の速度を計算し、モーターを動かします。

  delay(50); // M5Stackからの指令を待機
}
