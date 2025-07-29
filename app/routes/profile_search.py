from flask import Blueprint, request, render_template, session
from app.models.user import User
from sqlalchemy import or_

profile_search_bp = Blueprint('profile_search', __name__, template_folder='../../templates')

@profile_search_bp.route('/search')
def search():
    language = request.args.get('language')
    field = request.args.get('field')

    query = User.query

    #  LIKE検索
    if language:
        query = query.filter(User.language.ilike(f"%{language}%"))
    if field:
        query = query.filter(User.dev_field.ilike(f"%{field}%"))

    #  ログイン中のユーザーを除外
    if "user_id" in session:
        query = query.filter(User.id != session["user_id"])

    results = query.all()

    return render_template('main/profile_search.html', profiles=results)
