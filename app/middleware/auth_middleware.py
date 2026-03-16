import jwt
from functools import wraps
from flask import request, jsonify, current_app, g
from app.models.user import User


ROLE_HIERARCHY = {
    "viewer": 1,
    "operator": 2,
    "admin": 3,
    "owner": 4
}


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


def role_required(*allowed_roles):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            if not hasattr(g, "current_user"):
                return jsonify({"error": "Usuário não autenticado"}), 401

            user_role = g.current_user.role

            if user_role not in ROLE_HIERARCHY:
                return jsonify({"error": "Role inválida"}), 403

            user_level = ROLE_HIERARCHY[user_role]

            allowed_levels = [
                ROLE_HIERARCHY[r] for r in allowed_roles
            ]

            if user_level < min(allowed_levels):
                return jsonify({"error": "Acesso negado"}), 403

            return func(*args, **kwargs)

        return wrapper

    return decorator