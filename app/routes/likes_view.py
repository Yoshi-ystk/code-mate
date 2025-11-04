from flask import Blueprint, render_template, session, jsonify
from app.models.user import User
from app.models.likes import Likes
from app.models import db

# likes_view_bpは、いいねの送信と受信を表示するためのBlueprint
likes_view_bp = Blueprint("likes_view", __name__, template_folder="../../templates")


# いいねを送信したユーザーの一覧を取得
@likes_view_bp.route("/likes/sent")
def get_likes_sent():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "not logged in"}), 401

    likes = Likes.query.filter_by(from_user=user_id, matched=False).all()
    like_sent = []
    for l in likes:
        u = User.query.get(l.to_user)
        if u:
            like_sent.append(
                {
                    "id": u.id,
                    "name": u.name,
                    "email": u.email,
                    "language": u.language,
                    "dev_field": u.dev_field,
                    "experience": u.experience,
                    "introduction": u.introduction,
                    "image_path": u.image_path,
                }
            )
    # return jsonify(like_sent)
    return render_template("auth/likes_sent.html", like_sent=like_sent)


# いいねを受信したユーザーの一覧を取得
@likes_view_bp.route("/likes/received")
def get_likes_received():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "not logged in"}), 401

    likes = Likes.query.filter_by(to_user=user_id, matched=False).all()
    like_received = []
    for l in likes:
        u = User.query.get(l.from_user)
        if u:
            like_received.append(
                {
                    "id": u.id,
                    "name": u.name,
                    "email": u.email,
                    "language": u.language,
                    "dev_field": u.dev_field,
                    "experience": u.experience,
                    "introduction": u.introduction,
                    "image_path": u.image_path,
                }
            )
    return render_template("auth/likes_received.html", like_received=like_received)


# マッチ済みのユーザー一覧を取得
@likes_view_bp.route("/matched")
def get_matched():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "not logged in"}), 401

    likes = Likes.query.filter(
        Likes.matched == True,
        db.or_(Likes.to_user == user_id, Likes.from_user == user_id),
    ).all()
    matched_user = []
    seen_ids = set()

    for l in likes:
        other_user_id = l.to_user if l.from_user == user_id else l.from_user

        if other_user_id in seen_ids:
            continue  # すでに追加済みならスキップ

        u = User.query.get(other_user_id)
        if u:
            matched_user.append(
                {
                    "id": u.id,
                    "name": u.name,
                    "email": u.email,
                    "language": u.language,
                    "dev_field": u.dev_field,
                    "experience": u.experience,
                    "introduction": u.introduction,
                    "image_path": u.image_path,
                }
            )
        seen_ids.add(other_user_id)

    return render_template("auth/matched.html", matched_user=matched_user)
