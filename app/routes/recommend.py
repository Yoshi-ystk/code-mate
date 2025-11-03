from flask import Blueprint, session, jsonify
from app.models.user import User

recommend_bp = Blueprint("recommend", __name__, template_folder="../../templates")


@recommend_bp.route("/api/recommend")
def recommend_users():
    if "user_id" not in session:
        return jsonify({"error": "not logged in"}), 401
    current_user = User.query.get(session["user_id"])
    if not current_user:
        return jsonify({"error": "user not found"}), 404
    recommended = User.query.filter(
        User.language == current_user.language,
        User.dev_field == current_user.dev_field,
        User.id != current_user.id,
    ).all()
    result = [
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
        for u in recommended
    ]
    return jsonify(result)
