import os
from flask import Flask, render_template, session, redirect
from config import Config
from app.models.user import db, User
from app.routes.auth import auth_bp
from app.routes.profile import profile_bp
from app.routes.recommend import recommend_bp
from app.routes.recommend_profile import recommend_profile_bp
from app.routes.like_push import like_push_bp
from app.routes.likes_view import likes_view_bp
from app.models.likes import Likes
from flask_migrate import Migrate
from app.routes.profile_search import profile_search_bp  # 検索機能追加7/26
from sqlalchemy.sql import func  # ランダムでおすすめユーザーを生成7/30


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "..", "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "..", "static"),
        static_url_path="/static",
    )
    app.config.from_object(Config)
    db.init_app(app)

    Migrate(app, db)

    # DBファイルとフォルダの自動作成
    db_path = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    # DBがなければテーブルを作成
    if not os.path.exists(db_path):
        with app.app_context():
            db.create_all()
            print("✅ Database and tables created successfully.")

    # Blueprint登録
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(recommend_bp)
    app.register_blueprint(recommend_profile_bp)
    app.register_blueprint(like_push_bp)
    app.register_blueprint(likes_view_bp)
    app.register_blueprint(profile_search_bp)  # 検索機能追加7/26

    #  ホーム画面（おすすめ表示）
    @app.route("/main")
    def main():
        if "user_id" not in session:
            return redirect("main.top")
        current_user = User.query.get(session["user_id"])
        if not current_user:
            return redirect("main.top")

        # マッチ済みの to_user 一覧を取得（from_userが current_user.id）
        matched_users_subquery = (
            db.session.query(Likes.to_user)
            .filter(Likes.from_user == current_user.id, Likes.matched == True)
            .subquery()
        )
        # いいねしたユーザーの一覧を取得（from_userが current_user.id）
        liked_users_subquery = (
            db.session.query(Likes.to_user)
            .filter(Likes.from_user == current_user.id)
            .subquery()
        )

        # おすすめユーザーを取得（マッチ済み、いいね済み除外）
        recommended = (
            User.query.filter(
                User.language == current_user.language,
                User.dev_field == current_user.dev_field,
                User.id != current_user.id,
                ~User.id.in_(matched_users_subquery),
                ~User.id.in_(liked_users_subquery),
            )
            .order_by(func.random())
            .limit(6)
            .all()
        )
        return render_template("main/main.html", profiles=recommended)

    # お問い合わせページへ遷移させる
    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        return render_template("main/contact.html")

    # 利用規約への遷移
    @app.route("/attention")
    def show_attention():
        return render_template("main/attention.html")

    return app
