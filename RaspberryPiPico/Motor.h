#ifndef MOTOR_H
#define MOTOR_H

#include <Arduino.h>

class Motor {
private:
  int enaPin;
  int in1Pin;
  int in2Pin;
  
public:
  // コンストラクタ（初期化）
  Motor(int ena, int in1, int in2);

  // セットアップ
  void setup();

  // 速度と方向を設定
  void setSpeed(int speed, bool forward);

  // 停止
  void stop();
};

#endif
