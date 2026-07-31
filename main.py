#main.py
import face_tracking_auth
import time


import client

from akari_client import AkariClient

from akari_client.config import (
   AkariClientConfig,
   JointManagerGrpcConfig,
   M5StackGrpcConfig,
)





import os#ディレクトリ内部を取得
import sys
import types

try:
    import pkg_resources
except ImportError:
    # pkg_resources がない場合（Python 3.13以降）、ダミーを作成してエラーを回避
    m = types.ModuleType("pkg_resources")
    # 顔認識モデルが実際に置かれているパスを直接指定
    m.resource_filename = lambda pkg, res: os.path.join(
        sys.prefix, "lib", "python3.13", "site-packages", "face_recognition_models", res
    )
    sys.modules["pkg_resources"] = m
# --- Python 3.13 互換性パッチ (ここまで) ---

import face_recognition



#from answer_yes import AnswerYes


import human_detection
import face_distance



def main():
    global reject_name
    reject_name = []


    # akari_client_configを引数にしてAkariClientを作成する。
    akari = AkariClient()

    joints = akari.joints
    m5 = akari.m5stack
    # サーボトルクをONする。
    joints.enable_all_servo()

    #AkariClient、m5stackのインスタンスを取得する

    #isSleep = False
    count = 0

    #human_detection.detect_human()#人検知システム　


    #print("検知終了")

    #client.JudgementClient()#これを受け取ったら次に進むので、これが待機と動作を制御する

    judgement_soil,judgement_temp,judgement_suntime = client.JudgementClient()#これを受け取ったら次に進むので、これが待機と動作を制御する

    print("judgement_soil:",judgement_soil)
    print("judgement_temp:",judgement_temp)
    print("judgement_suntime:",judgement_suntime)

    reject_name = []

    human_detection.detect_human(m5,joints,reject_name,judgement_soil,judgement_temp,judgement_suntime)#人検知機能

    #face_distance.face_distance()#人の距離検知


    #face_tracking_auth.face_tracking(m5,joints)


    # while(1):

    #     #client.RasPiClient()

        # judgement, soil, tempC, dt= client.RasPiClient()

        # print("judgement:"+ str(judgement))
        # print("soil:" + str(soil))
        # print("tempC:"+str(tempC))
        # print("dt:"+str(dt))
        #print("name:"+str(name))
        #print("status:"+str(status))


        
    #     if judgement == 1: #まず、人検知をしてみつけてからface_tracking_auth.face_tracking(m5,joints,judgement, soil, tempC)


    #         face_tracking_auth.face_tracking(m5,joints,judgement, soil, tempC, dt)

    #     break


if __name__ == "__main__":
    main()
