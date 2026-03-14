from flask import Blueprint, request, jsonify
from app.models.user import User
from app.services.auth_service import generate_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.json

    user = User.query.filter_by(email=data["email"]).first()

    if not user:
        return jsonify({"error": "Credenciais inválidas"}), 401

    token = generate_token(user)

    return jsonify({
        "token": token
    })