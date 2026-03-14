from flask import Blueprint, request, jsonify
from app.services.user_service import UserService

user_bp = Blueprint("users", __name__)


@user_bp.route("/users", methods=["POST"])
def create_user():

    data = request.json

    user = UserService.create_user(data)

    return jsonify({
        "id": str(user.id),
        "email": user.email
    })


@user_bp.route("/users", methods=["GET"])
def list_users():

    users = UserService.list_users()

    result = []

    for user in users:

        result.append({
            "id": str(user.id),
            "email": user.email,
            "role": user.role
        })

    return jsonify(result)