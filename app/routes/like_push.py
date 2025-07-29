from flask import Blueprint, request, jsonify, session
from app.models.user import User
from app.models.likes import Likes, db

like_push_bp = Blueprint("like_push", __name__)

@like_push_bp.route("/favorite/<int:user_id>", methods=["POST"])
def like_push(user_id):
    if "user_id" not in session:
        return jsonify({"error": "ログインしてください"}), 401

    current_user_id = session["user_id"]

    # 相手が先に自分にLikeしているかチェック
    reverse_like = Likes.query.filter_by(
        from_user=user_id, to_user=current_user_id
    ).first()

    matched_flag = False
    if reverse_like and not reverse_like.matched:
        matched_flag = True
        reverse_like.matched = True

    # 自分の「いいね」を登録（重複チェックもあると◎）
    existing_like = Likes.query.filter_by(
        from_user=current_user_id, to_user=user_id
    ).first()
    if existing_like:
        return jsonify({"message": "すでにいいねしています"}), 200

    new_like = Likes(from_user=current_user_id, to_user=user_id, matched=matched_flag)
    db.session.add(new_like)
    db.session.commit()

    return jsonify({"message": "いいねが送信されました", "matched": matched_flag})
