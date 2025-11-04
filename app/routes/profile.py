from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    current_app,
    url_for,
)
import os
from werkzeug.utils import secure_filename
from app.models.user import User, db

# Blueprint定義は最初に
profile_bp = Blueprint("profile", __name__, template_folder="../../templates")


# マイページ表示 & 編集（同じURLでGETとPOSTを処理）
@profile_bp.route("/my_profile", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])
    if not user:
        return redirect("/login")

    if request.method == "POST":
        # フォームから値を取得して更新
        user.name = request.form.get("name")
        user.gender = request.form.get("gender")
        user.language = request.form.get("language")
        user.dev_field = request.form.get("dev_field")
        user.experience = request.form.get("experience")
        user.introduction = request.form.get("introduction")

        # 画像アップロード処理
        image = request.files.get("image")  # HTMLと一致
        if image and image.filename:
            filename = secure_filename(image.filename)

            # ユーザー専用フォルダ作成
            user_folder = os.path.join(
                current_app.config["UPLOAD_FOLDER"], str(user.id)
            )
            os.makedirs(user_folder, exist_ok=True)

            # 古い画像削除
            if user.image_path:
                old_image_path = os.path.join(
                    current_app.static_folder, user.image_path
                )
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            # 新しい画像保存
            save_path = os.path.join(user_folder, filename)
            image.save(save_path)
            user.image_path = f"uploads/{user.id}/{filename}"

            # DBに相対パスを保存（staticからのパス）
            # user.image_path = f"uploads/{user.id}/{filename}"

        # DBにコミット
        db.session.commit()
        return redirect("/main")  # 編集後は/mainへ

    # GET時：テンプレートにユーザー情報を渡す
    print(f"DEBUG (GET): user.image_path before rendering: {user.image_path}")
    return render_template("profile/my_profile.html", user=user)
