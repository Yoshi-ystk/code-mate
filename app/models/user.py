# UserモデルとSQLAlchemyインスタンス（db）を定義

from app.models import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(30))
    gender = db.Column(db.String(10))
    language = db.Column(db.String(40))
    dev_field = db.Column(db.String(40))
    experience = db.Column(db.String(40))
    introduction = db.Column(db.Text)
    image_path = db.Column(db.String(60), default="default.png")
