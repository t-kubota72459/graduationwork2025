#include "Motor.h"

// セットアップ：ピンモード設定
void Motor::setup() {
  pinMode(_ena, OUTPUT);
  pinMode(_in1, OUTPUT);
  pinMode(_in2, OUTPUT);

  // 初期状態で停止
  stop();
}

// 停止
void Motor::stop() {
  analogWrite(_ena, 0); // 速度を0にする
}
