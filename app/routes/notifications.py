from flask import Blueprint, jsonify, request, session
from app.models.likes import Likes
from app.models.user import User, db

notifications_bp = Blueprint("notifications", __name__)


# ✅ 通知状態を返すAPI
@notifications_bp.route("/api/notifications", methods=["GET"])
def get_notifications():
    current_user_id = session.get("user_id")
    if not current_user_id:
        return jsonify({"error": "未ログイン"}), 401

    # マッチ済み（相手とマッチした場合）
    match_exists = (
        Likes.query.filter(
            Likes.to_user == current_user_id, Likes.matched == True
        ).count()
        > 0
    )

    # 自分がいいねした人
    liked_exists = Likes.query.filter(Likes.from_user == current_user_id).count() > 0

    # 自分にいいねした人
    got_liked_exists = Likes.query.filter(Likes.to_user == current_user_id).count() > 0

    return jsonify({"match": match_exists, "got_liked": got_liked_exists})


# ✅ クリックで通知を既読扱いにするAPI（簡易）
@notifications_bp.route("/api/notifications/read", methods=["POST"])
def mark_notifications_read():
    data = request.json
    # ここでは既読処理はフロント側でベルを消すだけ（DBは今回は操作しない）
    return jsonify({"message": "既読化しました"})
