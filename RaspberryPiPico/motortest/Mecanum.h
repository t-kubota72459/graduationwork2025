#ifndef MECANUM_H
#define MECANUM_H
#include "Motor.h"

#pragma once

class Mecanum {
private:
    Motor* fl; // 前左
    Motor* fr; // 前右
    Motor* rl; // 後左
    Motor* rr; // 後右

public:
    // コンストラクタ：4つのモーターを登録する
    Mecanum(Motor& m_fl, Motor& m_fr, Motor& m_rl, Motor& m_rr)
        : fl(&m_fl), fr(&m_fr), rl(&m_rl), rr(&m_rr) {}

     /**
     * setup() 関数
     */
    void setup() {
        fl->setup();
        fr->setup();
        rl->setup();
        rr->setup();
    }

    void stop() {
        fl->stop();
        fr->stop();
        rl->stop();
        rr->stop();
    }

     /**
     * ロボットを動かすメイン関数
     * @param x 左右移動 (-100 〜 100)
     * @param y 前後移動 (-100 〜 100)
     * @param z 旋回     (-100 〜 100)
     */
    void drive(int forward, int strafe, int turn) {
        int fl_speed = int(limit( forward + strafe + turn) / 100.0f * 255.0f);
        int fr_speed = int(limit(-forward + strafe - turn) / 100.0f * 255.0f);
        int rl_speed = int(limit(-forward + strafe + turn) / 100.0f * 255.0f);
        int rr_speed = int(limit( forward + strafe - turn) / 100.0f * 255.0f);

        Serial.print("fl= ");
        Serial.print(fl_speed);
        Serial.print("| fr= ");
        Serial.print(fr_speed);
        Serial.print("| rl= ");
        Serial.print(rl_speed);
        Serial.print("| rr= ");
        Serial.print(rr_speed);
        Serial.println("");

        // 各モーターに出力
        fl->setSpeed(abs(fl_speed), fl_speed > 0);
        fr->setSpeed(abs(fr_speed), fr_speed > 0);
        rl->setSpeed(abs(rl_speed), rl_speed > 0);
        rr->setSpeed(abs(rr_speed), rr_speed > 0);
    }

private:
    // 速度が範囲外（例：-100〜100）に出ないようにガードする関数
    int limit(int speed) {
        if (speed > 100) return 100;
        if (speed < -100) return -100;
        return speed;
    }
};
#endif