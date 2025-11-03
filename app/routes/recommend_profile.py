from flask import Blueprint, render_template, session, request, jsonify
from app.models.user import User
from app.models.likes import Likes

# ユーザープロフィール表示にユーザー情報を渡すファイル
recommend_profile_bp = Blueprint("recommend_profile", __name__, template_folder="../../templates")

@recommend_profile_bp.route("/user/<int:user_id>")
def recommend_profile(user_id):
    user = User.query.get_or_404(user_id)
    # ログイン中のユーザーID
    current_user_id = session["user_id"]

    # この相手をいいねしているかを判定
    liked = Likes.query.filter_by(from_user=current_user_id, to_user=user_id).first() is not None

    return render_template("main/user_profile.html", user=user, liked=liked)
