#include "Motor.h"

// コンストラクタ：ピン番号を記憶
Motor::Motor(int ena, int in1, int in2) 
  : enaPin(ena), in1Pin(in1), in2Pin(in2) {}

// セットアップ：ピンモード設定
void Motor::setup() {
  pinMode(enaPin, OUTPUT);
  pinMode(in1Pin, OUTPUT);
  pinMode(in2Pin, OUTPUT);

  // 初期状態で停止
  stop();
}

/**
 * 速度と方向を同時に設定する
 * @param speed     0～255の速度
 * @param forward   true=正転, false=逆転
 */
void Motor::setSpeed(int speed, bool forward) {
  // 回転方向の設定
  if (forward) {
    digitalWrite(in1Pin, HIGH);
    digitalWrite(in2Pin, LOW);
  } else {
    digitalWrite(in1Pin, LOW);
    digitalWrite(in2Pin, HIGH);
  }
  
  // 速度の設定 (PWM)
  analogWrite(enaPin, speed);
}

// 停止
void Motor::stop() {
  analogWrite(enaPin, 0); // 速度を0にする
}
