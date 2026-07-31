#face_tracking_auth.py

# face_recognitionを使用した顔認識の例
import face_recognition


import argparse
import threading
import time

import psutil

from queue import Empty

from pathlib import Path
from queue import Queue
from time import sleep
from typing import Any
from datetime import datetime

import blobconverter
import cv2
import depthai as dai
import numpy as np
from akari_client import AkariClient
from utils.priorbox import PriorBox
from utils.utils import draw

from akari_client.position import Positions
from akari_client.color import Colors, Color


import face_recognition
import pickle







from gtts import gTTS 
import os





from answer_yes import AnswerYes


import re


import main






pan_target_angle = 0.0
tilt_target_angle = 0.0

setting_time = 15
soil_threshold = 700
tempC_threshold_min = 20
tempC_threshold_max = 32

running1 = True
running2 = True
running3 = True
running4 = True

# resize input to smaller size for faster inference
NN_WIDTH, NN_HEIGHT = 160, 120
VIDEO_WIDTH, VIDEO_HEIGHT = 320, 240


# 顔追従するクラス
class FaceTracker:
    """face tracking class"""

    def __init__(self,joints,m5) -> None:
        global pan_target_angle
        global tilt_target_angle

        self.joints = joints  #main.pyより、joints = akari.joints
        self.m5 = m5

        self._default_x = 0
        self._default_y = 0

        # サーボトルクON
        self.joints.enable_all_servo()
        # モータ速度設定
        self.joints.set_joint_velocities(pan=10, tilt=10)
        # モータ加速度設定
        self.joints.set_joint_accelerations(pan=30, tilt=30)

        # Initialize motor position
        # self.joints.move_joint_positions(pan=0, tilt=0)
        # while True:
        #     if (
        #         abs(self.joints.get_joint_positions()["pan"] - self._default_x) <= 0.087 #absは絶対値
        #         and abs(self.joints.get_joint_positions()["tilt"] - self._default_y)
        #         <= 0.087
        #     ):
        #         break
        self.currentMotorAngle = self.joints.get_joint_positions()

        # Dynamixel Input Value
        pan_target_angle = self.currentMotorAngle["pan"]
        tilt_target_angle = self.currentMotorAngle["tilt"]

    def _tracker(self) -> None:
        global pan_target_angle
        global tilt_target_angle
        global running1
        global running2
        global running3
        global running4

        running1 = True
        running2 = True
        running3 = True
        running4 = True

        #count3 = 0

        global tracking_enabled

        tracking_enabled = True

        while True:

            #count3 += 1

            #if count3 == 1:
                #data = self.m5.get()

            #if count3 %100 == 0:
                #data = self.m5.get()

            if tracking_enabled == False:
                sleep(2)

            elif tracking_enabled:
                self.joints.move_joint_positions(pan=pan_target_angle, tilt=tilt_target_angle)

            sleep(0.01)

            #if(data["brightness"]>3500):
                #running3 = False
                #break
            
            #if(running1 == False or running2 == False or running4 == False):
                #break

#-----------------------------------------------------------------------------

class DirectionUpdater: #カメラ画像から顔の位置を読み取り、次に首をどの角度に向けるべきか計算する担当
    """Update direction from face info"""

    _H_PIX_WIDTH = VIDEO_WIDTH
    _H_PIX_HEIGHT = VIDEO_HEIGHT

    #顔が画面中央から 0.1（10%）以上ズレないと首を動かしません。
    _PAN_THRESHOLD = 0.1
    _TILT_THRESHOLD = 0.1

    #中心位置
    _pan_dev = 0
    _tilt_dev = 0

    # モータゲインの最大幅。追従性の最大はここで変更 ズレに対してどれだけ大きく首を動かすか これ以上大きくすると、首が激しく振り切れてしまいます。
    _MAX_PAN_GAIN = 0.1
    _MAX_TILT_GAIN = 0.1

    # モータゲインの最小幅。追従性の最小はここで変更 どんなに顔が近くても、最低限これくらいの感度で追いかけます。
    _MIN_PAN_GAIN = 0.07
    _MIN_TILT_GAIN = 0.07

    # 顔の距離によってモータゲインを変化させる係数。
    _GAIN_COEF_PAN = 0.0001
    _GAIN_COEF_TILT = 0.0001

    #プログラム開始時の感度を、まずは最小値（0.07）に設定しておきます。
    _pan_p_gain = _MIN_PAN_GAIN
    _tilt_p_gain = _MIN_TILT_GAIN

    #左右（Pan）の限界
    _PAN_POS_MAX = 1.047
    _PAN_POS_MIN = -1.047

    #上下（Tilt）の限界
    _TILT_POS_MAX = 0.523
    _TILT_POS_MIN = -0.523

    #初期化関数　-> None は「この関数は値を返しません」
    def __init__(self) -> None:
        #時間管理用の変数
        global prev_time
        global cur_time

        self._face_x = 0
        self._face_y = 0
        self._face_width = 0
        self._face_height = 0

        #: float は、小数点を含む数値
        self._old_face_x: float = 0
        self._old_face_y: float = 0

    def _calc_p_gain(self) -> None: #遠くの顔への追従の際に、過剰に反応してしまい、首がガタツクのを防ぐ、近くの顔の移動に追いつくため

        #顔の横幅が広いほど、ゲイン（増幅率）を大きくして素早く反応させます。
        # 顔の距離によってモータゲインを変化させる係数 * 顔の横幅
        self._pan_p_gain = self._GAIN_COEF_PAN * self._face_width

        #最大、最小を超えないためのif文
        if self._pan_p_gain > self._MAX_PAN_GAIN:
            self._pan_p_gain = self._MAX_PAN_GAIN
        elif self._pan_p_gain < self._MIN_PAN_GAIN:
            self._pan_p_gain = self._MIN_PAN_GAIN

        #顔の縦幅が広いほど、ゲイン（増幅率）を大きくして素早く反応させます。
        self._tilt_p_gain = self._GAIN_COEF_TILT * self._face_width

        #最大、最小を超えないためのif文
        if self._tilt_p_gain > self._MAX_TILT_GAIN:
            self._tilt_p_gain = self._MAX_TILT_GAIN
        elif self._tilt_p_gain < self._MIN_TILT_GAIN:
            self._tilt_p_gain = self._MIN_TILT_GAIN

    def _face_info_cb(self, q_detection: Any, m5) -> None:
        global running1
        global running2
        global running3
        global running4

        running1 = True
        running2 = True
        running3 = True
        running4 = True

        m5stack = m5
        count2 = 0
        while True:

            #count2 += 1

            #if count2 == 1:
                #data = m5.get()

            #if count2 %100 == 0:
                #data = m5.get()

            #if(data["brightness"]>3500):
                #running2 = False
                #break

            #if(running1 == False or running3 == False or running4 == False):
                #break

            try:
                #キュー（箱）の中に溜まっているデータのうち、一番古いもの（次に処理すべきデータ）を1つ取り出します。
                #timeout=5:データが届くまで最大5秒間は待つ 
                self.detections = q_detection.get(timeout=5)

            except Empty:
                continue

            #q_detection.getで入手したデータを代入
            #顔の左上の座標を入手している
            self._face_x = self.detections[0]
            self._face_y = self.detections[1]

            self._face_width = self.detections[2]
            self._face_height = self.detections[3]

            #顔の中心座標を求める計算式
            self._set_goal_pos(
                self._face_x + self._face_width / 2,
                self._face_y + self._face_height / 2,
            )

            self._calc_p_gain()

    def _set_goal_pos(self, face_x: float, face_y: float) -> None: #首の角度をどれだけ動かすか
    #self._face_x + self._face_width / 2,顔の中心座標,self._face_y + self._face_height / 2,
        global pan_target_angle
        global tilt_target_angle

        if face_x >= 1000:
            face_x = 0
        if face_y >= 1000:
            face_y = 0

        pan_error = -(
            face_x + self._pan_dev - self._H_PIX_WIDTH / 2.0) / (
            self._H_PIX_WIDTH / 2.0
        )  
        #←真ん中から右に何ピクセルズレているか
        #- (マイナス符号): カメラの映像上の動きと、モーターの回転方向を合わせるための反転処理です。)
        # -1 ~ 1 の範囲で中心からズレた正規化　←　-100%~100%
            #self._pan_devはカメラの取り付けにズレが会った時などに調節するための数値であるため、一旦は無視

        #正規化　　画面の認識範囲x座標が0~640で、認識中央は320である。つまり、中央から、認識される顔のずれの範囲は-320~320 つまり、320で割れば-1~1に正規化できる。

        tilt_error = -(face_y + self._tilt_dev - self._H_PIX_HEIGHT / 2.0) / (
            self._H_PIX_HEIGHT / 2.0
        )  # -1 ~ 1

        """顔が画面中央から 0.1（10%）以上ズレないと首を動かしません。
        _PAN_THRESHOLD = 0.1
        _TILT_THRESHOLD = 0.1"""

        #absは絶対値

        if abs(pan_error) > self._PAN_THRESHOLD and not (face_x == self._old_face_x):
            pan_target_angle += self._pan_p_gain * pan_error
        #abs(pan_error) > self._PAN_THRESHOLD: ズレが設定値（0.1）より大きい時だけ動きます。
        #not (face_x == self._old_face_x): 前回のデータと全く同じ座標なら計算しません。無駄な計算を省きます。AI（カメラ）から新しい画像が届いていないのに、同じ古いデータを使って計算を繰り返すと、誤差が積み重なって首が勝手に滑り出してしまうことがあります。
        #_pan_p_gain:首を動かす速さ(正確には感度)
        #pan_error:正規化した中心からズレた座標
        #pan_target_angle:今の首の向き

        #つまり、顔の位置の遠さに比例して一歩を大きくして移動、一歩一歩をwhileループで高速にしてまるで滑らかに動いているように見せかけている。

        if pan_target_angle < self._PAN_POS_MIN:
            pan_target_angle = self._PAN_POS_MIN

        elif pan_target_angle > self._PAN_POS_MAX:
            pan_target_angle = self._PAN_POS_MAX

        if abs(tilt_error) > self._TILT_THRESHOLD and not (face_y == self._old_face_y):
            tilt_target_angle += self._tilt_p_gain * tilt_error

        if tilt_target_angle < self._TILT_POS_MIN:
            tilt_target_angle = self._TILT_POS_MIN

        elif tilt_target_angle > self._TILT_POS_MAX:
            tilt_target_angle = self._TILT_POS_MAX

        self._old_face_x = face_x
        self._old_face_y = face_y














def FaceRecognition(q_detection: Any,q_face: Any, m5) -> None:
    m5stack = m5
    count1 = 0


    # --------------- Arguments(引数) ---------------
    #コマンドライン引数とは、Pythonでプログラムを起動する際に指定する引数のことで、渡された引数はプログラム内で取得して使用することができます。
    parser = argparse.ArgumentParser()#argparse=コマンドライン引数を扱いやすくしてくれるモジュール
    parser.add_argument(
        "-nn",#ロボットの「顔認識の精度」や「処理の軽さ」を決めるAIモデル（脳）の切り替えスイッチのような役割
        "--nn_model",#"-nn", "--nn_model": オプションの名前です。実行時に python ファイル名.py -nn モデル名 のように使います。
        help="Provide model name or model path for inference",#help="...": 使い方がわからないときに python ファイル名.py -h と打つと表示される説明文です。
        default="face_detection_yunet_160x120",#何も指定しなかった場合に自動で選ばれるモデルです。ここでは「YuNet」という高速なモデルの「160x120サイズ版」が選ばれています。
        type=str,
    )
    parser.add_argument(
        "-conf",#略称？　信頼度
        "--confidence_thresh",#このオプションの名前です
        help="set the confidence threshold",
        default=0.6,#何も指定しない場合は「自信度が 60% 以上のものだけを顔として採用する」
        type=float,
    )
    parser.add_argument(
        "-iou",
        "--iou_thresh",#iouは閾値のこと
        help="set the NMS IoU threshold",
        default=0.3,
        type=float,
    )
    parser.add_argument(
        "-topk",
        "--keep_top_k",
        default=750,#自信度が高い順に最大750個までの候補を保持します。
        type=int,
        help="set keep_top_k for results outputing.",
        #AIの内部（今回のYuNetモデルなど）では、画面全体に網を張るようにして顔を探します。
        #最終的には「自信度（confidence）」や「重なり（IoU）」で絞り込まれますが、
        #その前段階で候補を切り捨てすぎないように、余裕を持った大きな数字（750）が設定されています。
    )

    #この一行を実行した瞬間に、実際に打ち込まれたコマンドが解析（パース）され、確定します。
    #例：python face_tracking.py -conf 0.8 と実行した場合、この行を通ることで args.confidence_thresh の中身が 0.8 に確定します。
    #何も入力されなかった場合は、すべて default で指定した値が使われます。
    args = parser.parse_args()






    nn_path = args.nn_model


    if not Path(nn_path).exists():
        print("No blob found at {}. Looking into DepthAI model zoo.".format(nn_path))
        nn_path = str(
            blobconverter.from_zoo(
                args.nn_model, shaves=6, zoo_type="depthai", use_cache=True
            )
        )
    #AIの「脳」にあたる学習済みモデル（.blobファイル）がパソコン内に見つからない場合に、
    #インターネット上の配布サイトから自動でダウンロードしてくる

    #args.nn_model:探してくるモデルの名前face_detection_yunet_160x120を指定
    #shaves:DepthAIカメラ（OAK-Dなど）の内蔵AIチップにある「SHAVE」という計算ユニットを何個使うかという設定です。←AIモデルに貸す感覚？
    #use_cache=True: 一度ダウンロードしたものは保存しておき、2回目以降はネットに繋がなくても使えるようにする設定です。

    # --------------- Pipeline ---------------　DepthAI（OAK-Dカメラ）内部の「データの流れ」を設計する
    # Start defining a pipeline　カメラ内部のチップで「撮影→加工→AI推論」を完結させます。この設計図のことを**「パイプライン」**と呼びます。
    pipeline = dai.Pipeline()#空の設計図本体を作成
    #depthai as dai
    pipeline.setOpenVINOVersion(version=dai.OpenVINO.VERSION_2021_4)#OpenVINO(AIによる推論処理を容易に開発できる無償の開発ツール)のバージョンを指定

    # Define a neural network that will detect faces
    detection_nn = pipeline.create(dai.node.NeuralNetwork)#パイプラインの中に「AI推論（神経回路網）」という部品を作ります。
    detection_nn.setBlobPath(nn_path)#nn_path:face_detection_yunet_160x120 をAI推論に読み込ませる
    detection_nn.setNumPoolFrames(4)#処理待ちをする画像の保存枠を4つ用意

    detection_nn.input.setBlocking(False)
    #Blocking = Trueの場合：AIの処理が長引いて、次の画像を受け取る準備ができていないとき、カメラ側は「AIの準備ができるまで、その場で待機（ブロック）」します。
    #Blocking = False の場合：AIが忙しければ、カメラは「あ、今は無理なのね」と判断して、その画像を捨てて次に進みます。
    #つまり、AIが画像を処理している間にカメラが入手した画像は捨て、AIの処理が終わった時点で最新となる画像をAIに渡す。
    #次の画像が来た時、前の処理が終わっていなければその画像を捨てて最新を優先します（リアルタイム性重視）。

    detection_nn.setNumInferenceThreads(2)#AIの推論に使うスレッド数を2つに設定し、並列処理を効率化します。
    #エンジンAが「画像1」を計算している間に、エンジンBが「画像2」を計算し始める。

    # Define camera
    cam = pipeline.create(dai.node.ColorCamera)#パイプラインの中に「カラーカメラ」という部品を作ります。
    cam.setPreviewSize(VIDEO_WIDTH, VIDEO_HEIGHT)#画像サイズを指定
    cam.setInterleaved(False)#画像形式をAIの処理が早い平面形式にする(TrueだとJPEGなどの標準形式)
    cam.setFps(60)#1秒間に40枚撮影する
    cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)#カメラセンサー自体の解像度をフルHD（1080P）に設定

    # Define manip #AIモデル（YuNet）は 160x120 という小さな画像しか受け取れないため、カメラの画像をリサイズする必要があります。
    manip = pipeline.create(dai.node.ImageManip)
    manip.initialConfig.setResize(NN_WIDTH, NN_HEIGHT)
    manip.initialConfig.setFrameType(dai.RawImgFrame.Type.BGR888p)#画像の色の形式を AIが理解できる「BGR形式」に設定
    manip.inputConfig.setWaitForMessage(False)#セットで使うはずの複数のデータが全部揃うまで、作業を一時停止して待機、せずに、来たものから処理

    # Create outputs
    #「カメラ映像」をPCへ出す出口を作り、"cam" という名前をつけます
    xout_cam = pipeline.create(dai.node.XLinkOut)
    xout_cam.setStreamName("cam")

    #「AIの解析結果」をPCへ出す出口を作り、"nn" という名前をつけます
    xout_nn = pipeline.create(dai.node.XLinkOut)
    xout_nn.setStreamName("nn")

    cam.preview.link(manip.inputImage)#カメラ映像をリサイズ加工機へ
    cam.preview.link(xout_cam.input)#カメラ映像（加工前）をそのままPCへ。
    manip.out.link(detection_nn.input)#リサイズした映像をAI推論へ。
    detection_nn.out.link(xout_nn.input)#AIの解析結果をPCへ。

    # --------------- Inference ---------------「設計図（パイプライン）」をカメラの実機に流し込み、実際にAIを動かして顔を見つけ、その結果をロボットに伝える「メインループ」
    # Pipeline defined, now the device is assigned and pipeline is started
    with dai.Device(pipeline) as device: #起動したカメラ実体のことを、これ以降のプログラムの中では device という名前で呼びますよ

        # Output queues will be used to get the rgb frames and nn data
        # from the outputs defined above
        #pipeline.create(dai.node.XLinkOut)で作った出口を以下のコードで開く
        q_cam = device.getOutputQueue("cam", 4, blocking=False)  # type: ignore　映像
        q_nn = device.getOutputQueue(name="nn", maxSize=4, blocking=False)  # type: ignore　AIの解析結果

        #start_time = time.time()#処理速度（FPS）を計算するためのタイマーとカウンターをリセット
        #counter = 0
        #fps = 0.0

        global running1
        global running2
        global running3
        global running4

        running1 = True
        running2 = True
        running3 = True
        running4 = True

        face_locations = []
        names = []

        while True:

            count1 += 1

            #if count1 == 1:
                #data = m5.get()

            #if count1 %100 == 0:
                #data = m5.get()

            in_frame = q_cam.get()#カメラから届いた最新の「画像データ」を入手
            in_nn = q_nn.get()#カメラから届いた最新の「AI生データ」を入手

            frame = in_frame.getCvFrame()#OpenCVの形式に変換

            # get all layers
            #ここでの"conf","iou","loc"は、このAIモデル（YuNet）を設計した人が決めた「出力データの名前」、あらかじめ決められたもの
            #「1076」AIモデル（YuNet）が画像をスキャンする時に使う「網の目の合計数」
            #reshape:1次元配列された生データx * y個をを（x, y）のように並び直してる
            conf = np.array(in_nn.getLayerFp16("conf")).reshape((1076, 2))#1076: 縦の行数（エリアの数）, 2: 横の列数（0列目：背景の確率、1列目：顔の確率）
            iou = np.array(in_nn.getLayerFp16("iou")).reshape((1076, 1))#重なり度合い（1個）が、1076行並びます。
            loc = np.array(in_nn.getLayerFp16("loc")).reshape((1076, 14))#14個の数字（四角形の座標 ＋ 目鼻口の点）が1セットになり、それが1076行並びます。

            # decode　AIが出した「生の座標」を、実際の画像の「ピクセル座標」に変換（デコード）します。この際、設定した自信度（0.6など）以下のものは捨てられます。
            pb = PriorBox(
                input_shape=(NN_WIDTH, NN_HEIGHT),#入力する画像
                output_shape=(frame.shape[1], frame.shape[0]),#出力する画像データ
            )
            dets = pb.decode(loc, conf, iou, args.confidence_thresh)#args.confidence_thresh:argsparseで定義した自信度(それ以下のものは切り捨て)
            #print(dets)
            # NMS
            if dets.shape[0] > 0:#「検出結果（dets）の中に、1つでも候補があるか？」を確認 numpy配列を入れた変数だから.shapeが使える？
                # NMS from OpenCV
                bboxes = dets[:, 0:4]#各候補の「四角形の位置（座標）」です。
                scores = dets[:, -1]#各候補の「自信度（スコア）」です。

                keep_idx = cv2.dnn.NMSBoxes(  #「ダブリ」を掃除
                    bboxes=bboxes.tolist(),#リスト型に変換
                    scores=scores.tolist(),#リスト型に変換
                    score_threshold=args.confidence_thresh,#自信度（score_threshold）が低いものを足切り
                    nms_threshold=args.iou_thresh,#その本物と重なり（nms_threshold）が大きい他の四角形を「同じ人の顔のダブリだ」とみなして消去
                    eta=1,#とりあえず、標準のまま(1)、マニアックな表記
                    top_k=args.keep_top_k,# parser.add_argument("-topk","--keep_top_k",~~~何個の候補を残すか
                )  # returns [box_num, class_num]
                

               # ★ここ重要：形を必ず統一
                if len(keep_idx) > 0:
                    keep_idx = np.array(keep_idx).reshape(-1)

                    dets = dets[keep_idx]

                    # ★ここで「2次元保証」
                    if dets.ndim == 1:
                        dets = np.expand_dims(dets, 0)

                    # ★1人だけ選ぶ（安全版）
                    best_idx = np.argmax(dets[:, -1])
                    best = dets[best_idx]





                    # x, y, w, h = best[0], best[1], best[2], best[3]

                    # bbox_area = w * h

                    # print("area:", bbox_area)

                    # if bbox_area > 0.15:
                    #     print("人が近づいた")

                    #     person_close_event.set()






                    # ★1人だけQueueへ
                    q_detection.put(best[:4])



                # Queueに最初の顔の座標を送信
                #q_detection.put(bboxes[0])

                # Queueに送信(顔認証用)
                #q_face.put((frame.copy(), dets.copy()))

                if q_face.full():
                    try:
                        q_face.get_nowait()
                    except Empty:
                        pass

                q_face.put_nowait((frame.copy(), dets.copy()))



            #counter += 1
            #if (time.time() - start_time) > 1:
                #fps = counter / (time.time() - start_time)

                #counter = 0
                #start_time = time.time()

            #if(data["brightness"]>3500): 
                #running1 = False
                #break

            #if(running2 == False or running3 == False or running4 == False):
                #break

            #if cv2.waitKey(1) == ord("q"):
                #break





def FaceAuth(q_face: Any, q_voice: Any, voice_started: threading.Event, wait_endvoice: threading.Event) -> None:#顔認識


    count1 = 99

    # ===== 顔データロード =====
    with open("encodings.pickle", "rb") as f:
        known_data = pickle.load(f)


    face_locations = []
    names = []

    #state = "search"

    while True:

        #person_close_event.wait()


        try:
            #キュー（箱）の中に溜まっているデータのうち、一番古いもの（次に処理すべきデータ）を1つ取り出します。
            #timeout=5:データが届くまで最大5秒間は待つ 
            frame, dets = q_face.get(timeout=5)

            #print(frame)
            #print(dets)
                
        except Empty:
            continue


        count1 += 1


        # Draw
        if dets.shape[0] > 0:

            if dets.ndim == 1:#「顔が1人しか見つからなかった時」のための補正です。
                dets = np.expand_dims(dets, 0)
                #「複数の顔（リストのリスト）」を想定して動きますが、1人だけだとデータが「1つの顔（ただのリスト）」という形になってしまいます。これだと後の処理でエラーが出るため、np.expand_dims を使って**「1人だけのリスト」という二重構造**に無理やり整えています。


            # YuNetの検出結果(dets)を face_recognition 形式 [(top, right, bottom, left), ...] に変換
            #face_locations = []


            #if count1 == 1:

                # for d in dets:
                #     YuNetの座標 [x, y, w, h] を取得
                #     x, y, w, h = d[0].astype(int), d[1].astype(int), d[2].astype(int), d[3].astype(int)
                #     face_recognitionは(top, right, bottom, left)の順番
                #     face_locations.append((y, x + w, y + h, x))

                # 顔の特徴量を抽出
                # rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
                # names = []
                # for encoding in encodings:
                #     matches = face_recognition.compare_faces(known_data["encodings"], encoding)
                #     name = "Unknown"
                #     if True in matches:
                #         matched_idxs = [i for (i, b) in enumerate(matches) if b]
                        #name = known_data["names"][matched_idxs[0]]
                    #names.append(name)

                # 描画処理
                #for ((top, right, bottom, left), name) in zip(face_locations, names):
                    # 枠と名前
                    #cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    #y = top - 15 if top - 15 > 15 else top +15
                    #cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)


            if count1 %100 == 0:

                face_locations = []
                names = []

                if count1 == 100:
                    wait_endvoice.set()

                wait_endvoice.wait()

                print("TrueになったのでFaceAuthを実行")

                #for d in dets:
                d = dets[0]
                # YuNetの座標 [x, y, w, h] を取得
                x, y, w, h = d[0].astype(int), d[1].astype(int), d[2].astype(int), d[3].astype(int)
                # face_recognitionは(top, right, bottom, left)の順番
                face_locations.append((y, x + w, y + h, x))

                # 顔の特徴量を抽出
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                print("encoding開始")

                encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                print("encoding終了")

            
                names = []
                for encoding in encodings:
                    print("比較開始")
                    matches = face_recognition.compare_faces(known_data["encodings"], encoding)
                    print("比較終了")
                    name = "Unknown"
                    if True in matches:
                        matched_idxs = [i for (i, b) in enumerate(matches) if b]
                        name = known_data["names"][matched_idxs[0]]
                    names.append(name)

                    #print(names)

                    names_str = ",".join(names)

                    #q_voice.put(names_str)

                    if q_voice.full():
                        try:
                            q_voice.get_nowait()
                        except Empty:
                            pass

                    q_voice.put_nowait((names_str))

                    print("q_voice送信完了")

                # 描画処理
                for ((top, right, bottom, left), name) in zip(face_locations, names):
                    # 枠と名前
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    y = top - 15 if top - 15 > 15 else top +15
                    cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

                #cv2.imshow("OAK-D Face Recognition", frame)







                if not voice_started.is_set():#状態確認 falseの場合
                    print("FaceAuth: set前")
                    voice_started.set()#True
                    print("FaceAuth: set後")

                    #print(names_str)

                    #text="あなたは"+names_str+"さんですか？"

                    #tts = gTTS(text, lang="ja", slow=False)

                    #ファイルへ出力
                    #tts.save('yomiage.mp3')

                    #音声ファイルの読み込み
                    #os.system("mpg123 yomiage.mp3")

                #voice_started.clear()
                





            # # 描画処理
            # for ((top, right, bottom, left), name) in zip(face_locations, names):
            #     # 枠と名前
            #     cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            #     y = top - 15 if top - 15 > 15 else top +15
            #     cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

            # cv2.imshow("OAK-D Face Recognition", frame)
            #cv2.waitKey(1)

            



        

def SayVoice(q_voice: Any ,voice_started: threading.Event, wait_endvoice: threading.Event, m5, joints, reject_name,judgement_soil,judgement_temp,judgement_suntime) -> None:

    count = 0
    name = ""

    while True:


        print("SayVoice: wait開始")
        voice_started.wait()  # ←ここで待機
        wait_endvoice.clear()
        print("SayVoice: wait解除")

        

        print("TrueになったのでSayVoiceを実行")

        count += 1

        try:
            #キュー（箱）の中に溜まっているデータのうち、一番古いもの（次に処理すべきデータ）を1つ取り出します。
            #timeout=5:データが届くまで最大5秒間は待つ 
            newname = q_voice.get(timeout=5)

            names_str = re.sub(r"[0-9]+", "", newname)
                
        except Empty:
            continue



        if count == 1:

            text="あなたは"+names_str+"さんですか？"

            tts = gTTS(text, lang="ja", slow=False)

            #ファイルへ出力
            tts.save('yomiage.mp3')


            print("前回の名前:" + name)
            print("今回の名前" + names_str)



            #音声ファイルの読み込み
            os.system("mpg123 yomiage.mp3")

            name = names_str

            countM5 = 0


            while True:

                data = m5.get()

                if countM5 == 0:

                    print("M5表示処理開始")

                    m5.set_display_text("いいえ",pos_x=Positions.LEFT,pos_y=Positions.BOTTOM, refresh=True, size=4, text_color=Colors.BLACK)
                    m5.set_display_text("はい",pos_x=Positions.RIGHT,pos_y=Positions.BOTTOM, refresh=False, size=4, text_color=Colors.BLACK)
               

                if data["button_a"] == True:

                    text="ごめなさーーーーーーーーーい"

                    tts = gTTS(text, lang="ja", slow=False)

                    #ファイルへ出力
                    tts.save('yomiage.mp3')

                    #音声ファイルの読み込み
                    os.system("mpg123 yomiage.mp3")

                    time.sleep(2)

                    break


                if data["button_c"] == True:


                    for name in reject_name:

                        if name == names_str:
                            text = "何回もごめんねーー"
                            tts = gTTS(text, lang="ja", slow=False)
                            #ファイルへ出力
                            tts.save('yomiage.mp3')
                            #音声ファイルの読み込み
                            os.system("mpg123 yomiage.mp3")

                            tracking_enabled = False

                            client.AboutKachaka(1)

                            time.sleep(10)

                            human_detection.detect_human(m5,joints,reject_name,judgement_soil,judgement_temp,judgement_suntime)


                    answer_yes = AnswerYes(names_str, m5, joints,reject_name,judgement_soil,judgement_temp,judgement_suntime)

                    # hour = dt.hour

                    # if hour == setting_time:
                    #     answer_yes.request_sun()

                    # if soil > soil_threshold:
                    #     answer_yes.request_water()

                    # if tempC_threshold_min > tempC or tempC > tempC_threshold_max:
                    #     answer_yes.request_temp()

                    



                    answer_yes.which_request()

                    #break

                
                countM5 += 1

                time.sleep(3)

                

            countM5 = 0

            if not wait_endvoice.is_set():#状態確認 falseの場合
                wait_endvoice.set()#True

            voice_started.clear()






        

        elif names_str == name:

            print("前回の名前:" + name)
            print("今回の名前" + names_str)

            time.sleep(3)

            if not wait_endvoice.is_set():#状態確認 falseの場合
                wait_endvoice.set()#True

            voice_started.clear()

            






        elif names_str != name:

            text="あなたは"+names_str+"さんですか？"

            tts = gTTS(text, lang="ja", slow=False)

            #ファイルへ出力
            tts.save('yomiage.mp3')


            print("前回の名前:" + name)
            print("今回の名前" + names_str)



            #音声ファイルの読み込み
            os.system("mpg123 yomiage.mp3")

            name = names_str

            countM5 = 0


            while True:

                print("countM5:",countM5)

                data = m5.get()

                if countM5 == 0:

                    print("M5表示処理開始")

                    m5.set_display_text("いいえ",pos_x=Positions.LEFT,pos_y=Positions.BOTTOM, refresh=True, size=4, text_color=Colors.BLACK)
                    m5.set_display_text("はい",pos_x=Positions.RIGHT,pos_y=Positions.BOTTOM, refresh=False, size=4, text_color=Colors.BLACK)

               

                if data["button_a"] == True:

                    text="ごめんなさーーーーーーーーーい"

                    tts = gTTS(text, lang="ja", slow=False)

                    #ファイルへ出力
                    tts.save('yomiage.mp3')

                    #音声ファイルの読み込み
                    os.system("mpg123 yomiage.mp3")

                    time.sleep(2)

                    break


                if data["button_c"] == True:

                    for name in reject_name:

                        if name == names_str:
                            text = "何回もごめんねーー"
                            tts = gTTS(text, lang="ja", slow=False)
                            #ファイルへ出力
                            tts.save('yomiage.mp3')
                            #音声ファイルの読み込み
                            os.system("mpg123 yomiage.mp3")

                            tracking_enabled = False

                            client.AboutKachaka(1)

                            time.sleep(10)

                            human_detection.detect_human(m5,joints,reject_name,judgement_soil,judgement_temp,judgement_suntime)


                    answer_yes = AnswerYes(names_str, m5, joints, reject_name,judgement_soil,judgement_temp,judgement_suntime)

                    # hour = dt.hour

                    # if hour == setting_time:
                    #     answer_yes.request_sun()

                    # if soil > soil_threshold:
                    #     answer_yes.request_water()

                    # if tempC_threshold_min > tempC or tempC > tempC_threshold_max:
                    #     answer_yes.request_temp()

                    answer_yes.which_request()

                    break

                
                countM5 += 1

                time.sleep(3)

                

            countM5 = 0



            if not wait_endvoice.is_set():#状態確認 falseの場合
                wait_endvoice.set()#True

            voice_started.clear()









def face_tracking(m5,joints,reject_name,judgement_soil,judgement_temp,judgement_suntime) -> None:

    #データの受け渡しをするものがキュー
    q_detection: Any = Queue()
    #q_face: Any = Queue()
    q_face: Any = Queue(maxsize=1)
    q_voice: Any = Queue(maxsize=1)

    voice_started = threading.Event()
    wait_endvoice = threading.Event()

    face_tracker = FaceTracker(joints,m5)
    direction_updater = DirectionUpdater()


    t1 = threading.Thread(target=FaceRecognition, args=(q_detection,q_face,m5,))
    t2 = threading.Thread(target=direction_updater._face_info_cb, args=(q_detection,m5,))
    t3 = threading.Thread(target=face_tracker._tracker)
    #t4 = threading.Thread(target=About_Display, args=(m5,Now_time,))
    t5 = threading.Thread(target=FaceAuth, args=(q_face,q_voice,voice_started,wait_endvoice,))
    t6 = threading.Thread(target=SayVoice, args=(q_voice,voice_started,wait_endvoice,m5,joints,reject_name,judgement_soil,judgement_temp,judgement_suntime,))


    t1.start()
    t2.start()
    t3.start()
    #t4.start()
    t5.start()
    t6.start()


    t1.join()
    t2.join()
    t3.join()
    #t4.join()
    t5.join()
    t6.join()