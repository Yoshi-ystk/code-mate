import os

# Flaskアプリの設定（SECRET_KEY, DB URI, アップロード先ディレクトリなど）をまとめた設定ファイル
# app.config.from_object(Config)で一元的に設定を読み込めます

basedir = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")


class Config:
    SECRET_KEY = "secretkey123"  # セッション暗号化用のキー
    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{os.path.join(basedir, 'instance', 'users.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "app", "static", "uploads")
