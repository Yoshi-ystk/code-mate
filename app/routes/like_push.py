from flask import Blueprint, request, jsonify, session
from app.models.user import User
from app.models.likes import Likes, db

# Blueprint定義
like_push_bp = Blueprint("like_push", __name__)

# ==========================================
# ① いいね送信API
# ==========================================
@like_push_bp.route("/favorite/<int:user_id>", methods=["POST"])
def like_push(user_id):
    """
    - ログインユーザーが相手に「いいね」する処理
    - もし相手から先に「いいね」されていたら matched=True にしてマッチ成立
    - いいね登録時に通知の未読状態を is_read=False で保存
    """
    if "user_id" not in session:
        return jsonify({"error": "ログインしてください"}), 401

    current_user_id = session["user_id"]

    # 相手が先に自分にLikeしているかチェック
    reverse_like = Likes.query.filter_by(from_user=user_id, to_user=current_user_id).first()

    matched_flag = False
    if reverse_like and not reverse_like.matched:
        matched_flag = True
        reverse_like.matched = True
        reverse_like.is_read = False  # ✅ マッチしたら相手に未読通知

    # 自分の「いいね」を登録（重複チェック）
    existing_like = Likes.query.filter_by(from_user=current_user_id, to_user=user_id).first()
    if existing_like:
        return jsonify({"message": "すでにいいねしています"}), 200

    # ✅ 新しいいいねは必ず未読
    new_like = Likes(
        from_user=current_user_id,
        to_user=user_id,
        matched=matched_flag,
        is_read=False
    )
    db.session.add(new_like)
    db.session.commit()

    return jsonify({"message": "いいねが送信されました", "matched": matched_flag})


# ==========================================
# ② 通知状態確認API
# ==========================================
@like_push_bp.route("/api/notifications", methods=["GET"])
def notifications():
    """
    - ログインユーザーの未読通知状態を返す
    - match → マッチ通知（matched=Trueで未読）
    - got_liked → いいねされた通知（matched=Falseで未読）
    """
    if "user_id" not in session:
        return jsonify({"match": False, "got_liked": False})

    user_id = session["user_id"]
    # ✅ マッチ成立の未読通知
    match_unread = Likes.query.filter(
        Likes.matched == True,
        Likes.to_user == user_id,
        Likes.is_read == False
    ).count() > 0
    # ✅ 「いいねされた」未読通知（ただしまだマッチしていない）
    got_liked_unread = Likes.query.filter(
        Likes.to_user == user_id,
        Likes.matched == False,
        Likes.is_read == False
    ).count() > 0

    return jsonify({
        "match": match_unread,
        "got_liked": got_liked_unread
    })


# ==========================================
# ③ 既読処理API
# ==========================================
@like_push_bp.route("/api/notifications/read", methods=["POST"])
def mark_read():
    """
    - 通知を既読にする処理
    - type=match → マッチ通知を既読化
    - type=got_liked → いいねされた通知を既読化
    """
    if "user_id" not in session:
        return jsonify({"error": "ログインしてください"}), 401

    data = request.get_json()
    notif_type = data.get("type")
    user_id = session["user_id"]

    if notif_type == "match":
        # ✅ マッチ通知を既読化 
        Likes.query.filter(
            Likes.matched == True,
            Likes.to_user == user_id
        ).update({"is_read": True})
    elif notif_type == "got_liked":
        # ✅ いいね通知を既読化（まだマッチしていないもの）
        Likes.query.filter(
            Likes.to_user == user_id,
            Likes.matched == False
        ).update({"is_read": True})

    db.session.commit()
    return jsonify({"message": "既読にしました"})