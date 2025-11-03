from app.models import db
from sqlalchemy.sql import func


class ChatMessage(db.Model):
    __tablename__ = "chatmessage"
    id = db.Column(db.Integer, primary_key=True)
    room = db.Column(db.String(100), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ChatMessage {self.id}>"
