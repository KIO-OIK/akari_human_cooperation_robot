#!/usr/bin/env python3

import argparse
import json
import time
from pathlib import Path
from typing import Any, List, Tuple, cast

import blobconverter
import cv2
import depthai as dai
import numpy as np

from akari_client import AkariClient

from akari_client.config import (
   AkariClientConfig,
   JointManagerGrpcConfig,
   M5StackGrpcConfig,
)


from gtts import gTTS 
import os

import threading

import time

# Get argument first
configPathDefault = str(
    (Path(__file__).parent / Path("yolov4tiny_coco_416x416.json"))
    .resolve()
    .absolute()
)
parser = argparse.ArgumentParser()
parser.add_argument(
    "-n",
    "--nnPath",
    nargs="?",
    help="Path to YOLO detection network blob",
    default="yolov4_tiny_coco_416x416",
)
parser.add_argument(
    "-c",
    "--configPath",
    nargs="?",
    help="Path to mobilenet detection label",
    default=configPathDefault,
)
args = parser.parse_args()

# get model path
nnPath = args.nnPath
if not Path(nnPath).exists():
    print("No blob found at {}. Looking into DepthAI model zoo.".format(nnPath))
    nnPath = str(
        blobconverter.from_zoo(
            args.nnPath, shaves=6, zoo_type="depthai", use_cache=True
        )
    )
if not Path(args.configPath).exists():
    raise ValueError("Path {} does not exist!".format(args.configPath))
with Path(args.configPath).open() as f:
    config = json.load(f)
nnConfig = config.get("nn_config", {})
width = 416 #YOLOv4-tiny標準サイズ
height = 416
# parse input shape
if "input_size" in nnConfig:
    width, height = tuple(map(int, nnConfig.get("input_size").split("x")))
# tiny yolo v4 label texts
labelMap = config["mappings"]["labels"]
metadata = nnConfig.get("NN_specific_metadata", {})#YOLO固有設定

syncNN = True#カメラ画像と推論結果を同期させる

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
camRgb = pipeline.create(dai.node.ColorCamera)
detectionNetwork = cast(
    dai.node.YoloDetectionNetwork, pipeline.create(dai.node.YoloDetectionNetwork)
)#YOLO推論ノード
xoutRgb = pipeline.create(dai.node.XLinkOut)#PCへ画像送信用
nnOut = pipeline.create(dai.node.XLinkOut)#PCへ検出結果送信用

xoutRgb.setStreamName("rgb")
nnOut.setStreamName("nn")

# Properties
camRgb.setPreviewSize(width, height)#リサイズ
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)#解像度
camRgb.setInterleaved(False)#BGR平面形式
camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)#OpenCV互換BGR
camRgb.setFps(40)#40FPS

# Network specific settings
detectionNetwork.setConfidenceThreshold(metadata.get("confidence_threshold", {}))#確信度しきい値
detectionNetwork.setNumClasses(metadata.get("classes", {}))#データセットの種類数
detectionNetwork.setCoordinateSize(metadata.get("coordinates", {}))#BBoxの座標数4
detectionNetwork.setAnchors(metadata.get("anchors", {}))
detectionNetwork.setAnchorMasks(metadata.get("anchor_masks", {}))
detectionNetwork.setIouThreshold(metadata.get("iou_threshold", {}))#重複ボックス関連
detectionNetwork.setBlobPath(nnPath)
detectionNetwork.setNumInferenceThreads(2)#推論処理を2スレッドで実行
detectionNetwork.input.setBlocking(False)#新しいフレームが来たら即処理

# Linking
camRgb.preview.link(detectionNetwork.input)
if syncNN:
    detectionNetwork.passthrough.link(xoutRgb.input)
else:
    camRgb.preview.link(xoutRgb.input)

detectionNetwork.out.link(nnOut.input)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:
    # Output queues will be used to get the rgb frames and nn data
    # from the outputs defined above

    qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)  # type: ignore
    qDet = device.getOutputQueue(name="nn", maxSize=4, blocking=False)  # type: ignore

    frame = None#現在画像
    detections: List[Any] = []#検出結果リスト
    startTime = time.monotonic()
    counter = 0
    color2 = (255, 255, 255)

    # nn data, being the bounding box locations, are in <0..1> range -
    # they need to be normalized with frame width/height
    def frameNorm(frame: Any, bbox: Tuple[Any, Any, Any, Any]) -> Any:#正規化されているので変換
        normVals = np.full(len(bbox), frame.shape[0])
        normVals[::2] = frame.shape[1]
        return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)

    def displayFrame(name: str, frame: object) -> None:
        color = (255, 0, 0)
        for detection in detections:
            bbox = frameNorm(
                frame, (detection.xmin, detection.ymin, detection.xmax, detection.ymax)
            )
            cv2.putText(#物体の名前を表示
                frame,
                labelMap[detection.label],
                (bbox[0] + 10, bbox[1] + 20),
                cv2.FONT_HERSHEY_TRIPLEX,
                0.5,
                255,
            )
            cv2.putText(#信頼度表示
                frame,
                f"{int(detection.confidence * 100)}%",
                (bbox[0] + 10, bbox[1] + 40),
                cv2.FONT_HERSHEY_TRIPLEX,
                0.5,
                255,
            )
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
        # Show the frame
        cv2.imshow(name, frame)



    def servo():

        # akari_client_configを引数にしてAkariClientを作成する。
        akari = AkariClient()

        joints = akari.joints
        #m5 = akari.m5stack
        # サーボトルクをONする。
        joints.enable_all_servo()


        count = 0

        while stop_event.is_set():

            count += 1

            joints.set_joint_velocities(pan=5,tilt=5)

            if count % 2 == 0:
                joints.move_joint_positions(pan=0.6, tilt=0.3)

                time.sleep(3)

            if count % 2 == 1:
                joints.move_joint_positions(pan=-0.6, tilt=0.3)

                time.sleep(3)

    stop_event = threading.Event()
    stop_event.set()

    thread_1 = threading.Thread(target=servo)

    thread_1.start()

    found = False

    while True:


        if syncNN:#同期していたら
            inRgb = qRgb.get()#画像取得
            inDet = qDet.get()#検出結果取得
        else:
            inRgb = qRgb.tryGet()#データがなければNoneを返す
            inDet = qDet.tryGet()#データがなければNoneを返す

        if inRgb is not None:
            frame = inRgb.getCvFrame()
            cv2.putText(
                frame,
                "NN fps: {:.2f}".format(counter / (time.monotonic() - startTime)),
                (2, frame.shape[0] - 4),
                cv2.FONT_HERSHEY_TRIPLEX,
                0.4,
                color2,
            )

        if inDet is not None:
            detections = inDet.detections

            for detection in detections:
                dataname = labelMap[detection.label]
                print(dataname)

                if dataname == "persn":


                    text="人間はっけーーーーーーーん。そこの人。こっちに来てください。"

                    stop_event.clear()

                    tts = gTTS(text, lang="ja", slow=False)

                    #ファイルへ出力
                    tts.save('yolo.mp3')

                    #音声ファイルの読み込み
                    os.system("mpg123 yolo.mp3")




                    found = True
                    break

                
            counter += 1

        if frame is not None:
            displayFrame("rgb", frame)

        if cv2.waitKey(1) == ord("q"):
            break

        if found == True:
            break
