from models import db

# ------ DB作成 ------
def init_db():              # DBを作成するinit_db()関数を定義
    with app.app_context(): # Flaskの「アプリケーションコンテキスト」を有効化
                            # これにより「db.session」を使った操作が可能になる
        print('テーブルを作成')
        #db.drop_all()       # 既存のテーブルを全て削除（初期化）
        db.create_all()     # モデル（BookLog）に基づいてテーブルを作成

        # データ作成
        print("データ登録：実行")
        student_log01 = Student(name='nozaka',cooperate_count=0,cansel_count=0) # BookLogクラス（モデル）をインスタンス生成し、book_log01に代入
        student_log02 = Student(name='',cooperate_count=0,cansel_count=0)			# 同上
        student_log03 = Student(name='',cooperate_count=0,cansel_count=0)  # 同上
        db.session.add_all([book_log01, book_log02, book_log03]) # まとめて登録
        db.session.commit() # データベースに保存






        #book = BookLog.query.get(1) #ID１番を取得する
        #book.count += 1 #カウントをプラスする
        #db.session.commit() #更新











        # ------ テーブル操作（CRUD操作） ------
# 登録
def insert(): # データを登録するinsert()関数を定義
    print('1件登録')
    with app.app_context(): # Flaskの「アプリケーションコンテキスト」を有効化
        book_log04 = BookLog(title='博士の愛した数式') # BookLogクラスをインスタンス生成し、book_log04に代入
                                                      # 「title='博士の愛した数式'」はPythonのキーワード引数
        db.session.add(book_log04) # book_log04をセッションに追加
        db.session.commit()        # セッションをデータベースに反映（保存）
        print('登録 ->', book_log04)