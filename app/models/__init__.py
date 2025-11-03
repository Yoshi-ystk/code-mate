from flask_sqlalchemy import SQLAlchemy

# モデルを一元管理するファイル
db = SQLAlchemy()

from .user import User
from .likes import Likes
from .chat_messages import ChatMessage

__all__ = ["db", "User", "Likes", "ChatMessage"]
