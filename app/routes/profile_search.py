from flask import Blueprint, request, render_template, session
from app.models.user import User
from sqlalchemy import or_

profile_search_bp = Blueprint(
    "profile_search", __name__, template_folder="../../templates"
)


@profile_search_bp.route("/search")
def search():
    language = request.args.get("language")
    dev_field = request.args.get("dev_field")

    query = User.query

    #  LIKE検索
    if language:
        query = query.filter(User.language.ilike(f"%{language}%"))
    if dev_field:
        query = query.filter(User.dev_field.ilike(f"%{dev_field}%"))

    #  ログイン中のユーザーを除外
    if "user_id" in session:
        query = query.filter(User.id != session["user_id"])

    results = query.all()

    return render_template("main/profile_search.html", profiles=results)
