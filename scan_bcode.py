import depthai as dai
import cv2
from pyzbar.pyzbar import decode
import time

# ===== クールダウン設定 =====
last_detected = {}
COOLDOWN = 60  # 秒

# ===== DepthAIパイプライン作成 =====
pipeline = dai.Pipeline()

cam = pipeline.createColorCamera()


cam.setPreviewSize(640, 480)
cam.setInterleaved(False)
cam.setFps(60)

xout = pipeline.createXLinkOut()
xout.setStreamName("video")
cam.preview.link(xout.input)

print("起動しました（qキーで終了）")

# ===== デバイス起動 =====
with dai.Device(pipeline) as device:
    q = device.getOutputQueue(name="video", maxSize=4, blocking=False)

    try:
        while True:
            inFrame = q.get()
            frame = inFrame.getCvFrame()

            # ===== バーコード検出 =====
            barcodes = decode(frame)

            for barcode in barcodes:
                data = barcode.data.decode('utf-8')
                current_time = time.time()

                last_time = last_detected.get(data, 0)

                # クールダウン中ならスキップ
                if current_time - last_time < COOLDOWN:
                    continue

                # ===== 新規検出 =====
                print("読み取り結果:", data)
                last_detected[data] = current_time

                # 枠描画
                x, y, w, h = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # テキスト表示
                cv2.putText(frame, data, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 255, 0), 2)

            # ===== 画面表示 =====
            cv2.imshow("OAK-D Barcode Reader", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nCtrl+Cで終了しました")

cv2.destroyAllWindows()