import depthai as dai
import face_recognition
import pickle
import cv2

# ===== 顔データロード =====
with open("encodings.pickle", "rb") as f:
    data = pickle.load(f)

# ===== DepthAI パイプライン =====
pipeline = dai.Pipeline()

cam = pipeline.createColorCamera()
cam.setPreviewSize(320, 240)
cam.setInterleaved(False)
cam.setFps(30)

xout = pipeline.createXLinkOut()
xout.setStreamName("rgb")
cam.preview.link(xout.input)

print("顔認証を開始します...（qで終了）")

# ===== デバイス起動 =====
with dai.Device(pipeline) as device:
    q = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

    while True:
        in_frame = q.get()
        frame = in_frame.getCvFrame()

        # OpenCV → face_recognitionはRGB必須
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 顔検出
        boxes = face_recognition.face_locations(rgb_frame, model="hog")
        encodings = face_recognition.face_encodings(rgb_frame, boxes)

        names = []

        for encoding in encodings:
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            name = "Unknown"

            if True in matches:
                matched_idxs = [i for (i, b) in enumerate(matches) if b]
                name = data["names"][matched_idxs[0]]

            names.append(name)

        # 描画
        for ((top, right, bottom, left), name) in zip(boxes, names):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                        (0, 255, 0), 2)

        cv2.imshow("OAK-D Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()