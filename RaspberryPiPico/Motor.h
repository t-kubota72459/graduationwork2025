#ifndef MOTOR_H
#define MOTOR_H

#include <Arduino.h>

class Motor {
  public:
    // コンストラクタ（初期化）
    Motor(int ena, int in1, int in2, bool reversed = false) 
      : _ena(ena), _in1(in1), _in2(in2), _reversed(reversed) {}
    
    // セットアップ
    void setup();

    // 速度と方向を設定
    void setSpeed(int speed, bool forward) {
      // ここで反転フラグを反映させる
      bool actualForward = _reversed ? !forward : forward;
        
      digitalWrite(_in1, actualForward ? HIGH : LOW);
      digitalWrite(_in2, actualForward ? LOW : HIGH);
      analogWrite(_ena, speed);
    }
  
    // 停止
    void stop();

  private:
    int _ena, _in1, _in2;
    bool _reversed;
};
#endif
