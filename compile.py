#compile.py
import face_tracking_auth
import time


import client
# from client import socket_loop
# from client import scheduler

from akari_client import AkariClient

from akari_client.config import (
   AkariClientConfig,
   JointManagerGrpcConfig,
   M5StackGrpcConfig,
)


import threading


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


from datetime import datetime
#from answer_yes import AnswerYes


import human_detection
import face_distance

import arduino_send_akari

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

    #human_detection.detect_human()#人検知システム　
    
    #judgement_soil,judgement_temp,judgement_suntime = client.JudgementClient()
    judgement_soil= 0
    judgement_temp = 0
    judgement_suntime = 0

    print("judgement_soil:",judgement_soil)
    print("judgement_temp:",judgement_temp)
    print("judgement_suntime:",judgement_suntime)

    re = []

    last_sent = None

    while True:
        tempC,soil = arduino_send_akari.main()
        print("tempC:", tempC)
        print("soil", soil)

        # now = datetime.now()

        # if now.second == 0:

        #     key = (now.hour, now.minute)

        #     if key != last_sent:#同じ時刻に何回も送られないように
        #         tempC,soil = arduino_send_akari.main()
        #         last_sent = key

        #         print("tempC:", tempC)
        #         print("soil", soil)


    # face_distance.face_distance(m5,joints,re)

    #human_detection.detect_human(m5,joints,re,judgement_soil,judgement_temp,judgement_suntime)

    #face_tracking_auth.face_tracking(m5,joints)
    # threading.Thread(target=socket_loop, daemon=True).start()
    # threading.Thread(target=scheduler, daemon=True).start()

    # while True:
    #     time.sleep(1)
    #     threading.Thread(target=socket_loop, daemon=True).start()
    #     threading.Thread(target=scheduler, daemon=True).start()

        # soil = SensorClient()







# judgement_soil: 0
# judgement_temp: 0
# judgement_suntime: 0
# ====================================
# AKARIセンサーサーバー起動
# 待受アドレス: 0.0.0.0
# 待受ポート  : 6001
# Arduinoの接続を待っています
# ====================================
# AKARIへ接続しました
# [2026-07-31 11:36:19] 6001番ポートへ接続されました: 172.31.14.7:57170

# ====================================
# [2026-07-31 11:36:19] Arduino接続
# 接続元: 172.31.14.7:57170
# ====================================
# [2026-07-31 11:37:00] Arduinoへ送信: GET_SENSOR_DATA

# ====================================
# AKARIがセンサーデータを受信しました
# 受信時刻       : 2026-07-31 11:37:00
# ------------------------------------
# 温度           : 26.9 ℃
# 土壌センサー   : 701
# 温度判定       : 0
# 土壌判定       : 1
# ====================================

# [2026-07-31 11:37:00] Arduinoが切断されました
# プログラムを終了しました
# tempC: 26.9
# soil 701
# Exception in thread Thread-3 (start_server):
# Traceback (most recent call last):
#   File "/usr/lib/python3.10/threading.py", line 1016, in _bootstrap_inner
# AKARIへ接続しました
#     self.run()
#   File "/usr/lib/python3.10/threading.py", line 953, in run
#     self._target(*self._args, **self._kwargs)
#   File "/home/aitclab2011/ダウンロード/akari_human_cooperation_robot-KIO/arduino_send_akari.py", line 484, in start_server
#     server_socket.bind(
# OSError: [Errno 98] Address already in use
# プログラムを終了しました
# tempC: 26.9
# soil 701


if __name__ == "__main__":
    main()
