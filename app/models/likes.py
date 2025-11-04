from app.models import db


# いいねとマッチした人を管理する、likesテーブル定義
class Likes(db.Model):
    __tablename__ = "likes"
    likes_id = db.Column(db.Integer, primary_key=True)
    from_user = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    to_user = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    matched = db.Column(db.Boolean, default=False)
    is_read = db.Column(db.Boolean, default=False)  # 通知の既読監視
