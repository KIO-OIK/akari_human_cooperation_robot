# face_recognitionを使用した顔認識の例
import face_recognition

# 既知の顔とそのエンコーディング
known_image = face_recognition.load_image_file('known_person.jpg')
known_encoding = face_recognition.face_encodings(known_image)[0]

# 認識したい画像を読み込む
unknown_image = face_recognition.load_image_file('unknown_person.jpg')
unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

# 顔の一致を比較
results = face_recognition.compare_faces([known_encoding], unknown_encoding)

if results[0]:
    print("同じ人物です！")
else:
    print("違う人物です。")