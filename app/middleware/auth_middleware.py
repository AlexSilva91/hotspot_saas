import jwt
from functools import wraps
from flask import request, jsonify, current_app, g
from app.models.user import User


def jwt_required():

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            auth_header = request.headers.get("Authorization")

            if not auth_header:
                return jsonify({"error": "Token não fornecido"}), 401

            try:

                token = auth_header.split(" ")[1]

                payload = jwt.decode(
                    token,
                    current_app.config["SECRET_KEY"],
                    algorithms=["HS256"]
                )

                user = User.query.get(payload["user_id"])

                if not user:
                    return jsonify({"error": "Usuário inválido"}), 401

                g.current_user = user
                g.tenant_id = user.tenant_id

            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expirado"}), 401

            except Exception:
                return jsonify({"error": "Token inválido"}), 401

            return func(*args, **kwargs)

        return wrapper

    return decorator