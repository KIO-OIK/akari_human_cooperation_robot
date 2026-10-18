#学習データの顔の特徴をエンコーディング

import pickle#pythonのオブジェクト、リストや辞書など、をファイルとして保存、読み込み
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


print("顔画像のエンコードを開始します...")
known_encodings = []
known_names = []

# known_facesディレクトリ内の各画像をループ
for image_name in os.listdir("known_faces"):#フォルダ内のファイル名を取り出す
    # 画像をロード
    image_path = os.path.join("known_faces", image_name)
    image = face_recognition.load_image_file(image_path)
    
    # 顔のエンコーディングを取得 (画像内の最初の顔)
    # 存在しない場合はスキップ
    encodings = face_recognition.face_encodings(image)
    if len(encodings) > 0:#顔が１個以上あれば
        encoding = encodings[0]#最初の顔を取得
        
        # エンコーディングと名前をリストに追加
        known_encodings.append(encoding)#顔の特徴データをknown_encodingsに追加
        known_names.append(os.path.splitext(image_name)[0]) # ファイル名から拡張子を除いたものを名前とする

# エンコーディングと名前をファイルに保存
data = {"encodings": known_encodings, "names": known_names}
with open("encodings.pickle", "wb") as f:#書き込み専用モードで開く
    f.write(pickle.dumps(data))#ファイル保存できる形式にへんかんし、書き込む

print("エンコードが完了しました。")
