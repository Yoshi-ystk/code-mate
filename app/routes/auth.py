from flask import Blueprint, render_template, request, redirect, session, current_app
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from app.models.user import User, db
from werkzeug.security import (
    check_password_hash,
)
import os

# ログイン、ユーザー登録、ログアウトのルーティングを担当
# user.pyのUserモデルとdbを利用

auth_bp = Blueprint("auth", __name__, template_folder="../../templates")


@auth_bp.route("/", methods=["GET", "POST"])
@auth_bp.route("/top", methods=["GET", "POST"])
def top():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect("/main")
        else:
            return render_template("auth/login_failed.html")
    return render_template("auth/top.html")


@auth_bp.route("/register_profile", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        name = request.form["name"]
        gender = request.form["gender"]
        language = request.form["language"]
        dev_field = request.form["dev_field"]
        experience = request.form["experience"]
        introduction = request.form["introduction"]

        # 既存ユーザー確認
        if User.query.filter_by(email=email).first():
            return "既に登録されています"

        # ユーザー作成
        user = User(
            email=email,
            password=password,
            name=name,
            gender=gender,
            language=language,
            dev_field=dev_field,
            experience=experience,
            introduction=introduction,
        )
        db.session.add(user)
        db.session.commit()

        # 画像アップロード
        image = request.files.get("image")
        if image and image.filename != "":
            filename = secure_filename(image.filename)
            user_folder = os.path.join(
                current_app.config["UPLOAD_FOLDER"], str(user.id)
            )
            os.makedirs(user_folder, exist_ok=True)

            # 古い画像削除（登録直後は不要だが安全のため）
            old_image = os.path.join(user_folder, filename)
            if os.path.exists(old_image):
                os.remove(old_image)

            # 保存
            save_path = os.path.join(user_folder, filename)
            image.save(save_path)

            # DBに保存
            user.image_path = f"uploads/{user.id}/{filename}"
            db.session.commit()

        session["user_id"] = user.id
        return redirect("/main")

    return render_template("auth/register_profile.html")


@auth_bp.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/top")
