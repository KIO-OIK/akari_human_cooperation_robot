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



from answer_yes import AnswerYes



def main():


    # akari_client_configを引数にしてAkariClientを作成する。
    akari = AkariClient()

    joints = akari.joints
    m5 = akari.m5stack
    # サーボトルクをONする。
    joints.enable_all_servo()

    #AkariClient、m5stackのインスタンスを取得する

    #isSleep = False
    count = 0


    while(1):

        #client.RasPiClient()

        judgement, soil, tempC, dt= client.RasPiClient()

        print("judgement:"+ str(judgement))
        print("soil:" + str(soil))
        print("tempC:"+str(tempC))
        print("dt:"+str(dt))
        #print("name:"+str(name))
        #print("status:"+str(status))


        
        if judgement == 1: #まず、人検知をしてみつけてからface_tracking_auth.face_tracking(m5,joints,judgement, soil, tempC)


            face_tracking_auth.face_tracking(m5,joints,judgement, soil, tempC, dt)

        break


if __name__ == "__main__":
    main()
