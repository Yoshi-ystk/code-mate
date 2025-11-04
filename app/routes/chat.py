from flask import Blueprint, render_template, session, redirect, url_for, request
from flask_login import current_user, login_required
from app.models import db
from app.models.likes import Likes
from app.models.chat_messages import ChatMessage
from app.extensions import socketio
from flask_socketio import send, emit, join_room, leave_room
from sqlalchemy import or_

chat_bp = Blueprint("chat", __name__)

from app.models.user import User


@chat_bp.route("/chat_list")
@login_required
def chat_list():
    my_id = session.get("user_id")
    likes = Likes.query.filter(
        or_((Likes.from_user == my_id), (Likes.to_user == my_id)), Likes.matched == True
    ).all()

    matched_users_ids = set()
    for like in likes:
        if like.from_user == my_id:
            matched_users_ids.add(like.to_user)
        else:
            matched_users_ids.add(like.from_user)

    matched_users = User.query.filter(User.id.in_(matched_users_ids)).all()

    return render_template("chat/chat_list.html", matched_users=matched_users)


@chat_bp.route("/chat/<int:user_id>")
@login_required
def chat_room(user_id):
    # --- 認証 ---
    # 1. セッションから現在のユーザーIDを取得
    my_id = session.get("user_id")
    # 2. チャット相手(user_id)と自分(my_id)がマッチングしているかDBで確認
    is_matched = Likes.query.filter(
        or_(
            (Likes.from_user == my_id) & (Likes.to_user == user_id),
            (Likes.from_user == user_id) & (Likes.to_user == my_id),
        ),
        Likes.matched == True,
    ).first()
    # 3. マッチングしていなければ、プロフィールページなどにリダイレクト
    if not is_matched:
        return redirect(url_for("profile.show", user_id=user_id))

    # --- チャット相手の情報を取得 ---
    other_user = User.query.get(user_id)

    # --- チャットルームIDの生成 ---
    # 必ず "小さいID_大きいID" の形式になるようにし、一意のルームIDを生成
    room_id = f"{min(my_id, user_id)}_{max(my_id, user_id)}"

    # --- 過去のメッセージ履歴を取得 ---
    past_messages_query = (
        ChatMessage.query.filter_by(room=room_id).order_by(ChatMessage.timestamp).all()
    )
    past_messages = [
        {"sender_id": msg.sender_id, "message": msg.message}
        for msg in past_messages_query
    ]

    return render_template(
        "chat/chat.html",
        user_id=user_id,
        room_id=room_id,
        past_messages=past_messages,
        other_user=other_user,
    )


# --- Socket.IO イベントハンドラ ---


@socketio.on("join")
def on_join(data):
    room = data["room"]
    join_room(room)
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    emit("status", {"msg": user.name + "さんが入室しました。"}, room=room)


@socketio.on("leave")
def on_leave(data):
    room = data["room"]
    leave_room(room)
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    emit("status", {"msg": user.name + "さんが退室しました。"}, room=room)


@socketio.on("message")
def handle_message(data):
    room = data["room"]
    message = data["message"]
    sender_id = session.get("user_id")

    # --- メッセージをDBに保存 ---
    new_message = ChatMessage(room=room, sender_id=sender_id, message=message)
    db.session.add(new_message)
    db.session.commit()

    emit("message", {"msg": message, "sender_id": sender_id}, room=room)
