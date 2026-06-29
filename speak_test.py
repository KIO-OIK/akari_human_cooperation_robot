from gtts import gTTS 
import os

#音声ファイルをAPIで取得する
text="こんにちはあああ"

tts = gTTS(text, lang="ja", slow=False)

#ファイルへ出力
tts.save('yomiage.mp3')

# 音声ファイルの読み込み
os.system("mpg123 yomiage.mp3")

str="かいよう"
text="あなたは"+str+"さんですか？"

tts = gTTS(text, lang="ja", slow=False)

#ファイルへ出力
tts.save('yomiage.mp3')

# 音声ファイルの読み込み
os.system("mpg123 yomiage.mp3")