import cv2
import depthai as dai

#カメラの設定　デバイスIDは0    OAK-Dカメラだとこれができない
cap = cv2.VideoCapture(20)

#繰り返しのためのwhile文
while True:
    #カメラからの画像取得
    ret, frame = cap.read()

    #”frame”の前にある”ret”には、画像の取得が成功したかどうかの結果が(True/Fales)の２値で格納されます。
    #print(ret)を実行することで、取得が成功したかを表示することが可能です。

    #カメラの画像の出力
    cv2.imshow('camera' , frame)

    #繰り返し分から抜けるためのif文
    key =cv2.waitKey(10)
    if key == 27:
        break

#メモリを解放して終了するためのコマンド
cap.release()
cv2.destroyAllWindows()