from flask_sqlalchemy import SQLAlchemy # SQLAlchemy：DBとPythonクラスを紐づけるライブラリ



# db変数を使用してSQLAlchemyを操作
db = SQLAlchemy(app) # SQLAlchemyオブジェクトをインスタンス生成して変数dbへ代入
    # このdbを使って「モデル定義」や「データベースへの登録・更新・削除」などの操作ができるようになる


# 協力してくれる人の候補テーブル
class Student(db.Model): # db.Modelクラスを継承したBookLogクラスの定義
    # テーブル名
    __tablename__ = 'student_logs'
    # Columnクラスを使ってテーブルの列を２つ定義
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) # 書籍ID（種キー, 連番）
    name = db.Column(db.String(200), nullable=False)				 # 書籍のタイトル（入力必須）]
    cooperate_count = db.Column(db.Integer, default=0)
    cansel_count = db.Column(db.Integer, default=0)
    # 表示用関数
    def __str__(self):
        return f"ID：{self.id} 名前：{self.title} 協力回数：{self.cooperate_count} 断った回数：{self.cansel_count}"