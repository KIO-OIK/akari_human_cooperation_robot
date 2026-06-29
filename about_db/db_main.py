import secrets							# セキュアなランダム値生成用の標準ライブラリ（Python 3.6以降推奨）
from pathlib import Path				# pathlibライブラリのPathクラスをインポート
from flask import Flask                 # Flaskをインポート
from flask_sqlalchemy import SQLAlchemy # SQLAlchemy：DBとPythonクラスを紐づけるライブラリ

from models import db

app = Flask(__name__)                   # Flaskアプリケーションのインスタンス生成






# ------ Flaskに関する設定 ------
# セッション保護用のランダムな秘密鍵を設定
app.config['SECRET_KEY'] = secrets.token_hex(24) #24バイトのランダムバイト列を作成し、SECRET_KEYというキー名で辞書に追加
#config属性：Flaskアプリの設定値を管理する辞書。app.config['キー名'] = 値 の形で、色々な設定項目を追加・変更できる



# DBファイルの設定
base_dir = Path(__file__).parent	# このスクリプトファイルがあるフォルダのパスを取得して、変数base_dirに代入
database = base_dir / 'partner.db'	# base_dir内のdata.sqliteというファイルへのパスを作成し、変数databaseに代入

app.config['SQLALCHEMY_DATABASE_URI'] = database	 # DBのパスをSQLALCHEMY_DATABASE_URIというキー名で辞書に追加
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # SQLAlchemyの「変更追跡機能」を無効化にしてメモリ使用を軽減

db.init_app(app)