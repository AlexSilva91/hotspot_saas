import jwt
from datetime import datetime, timedelta
from flask import current_app


def generate_token(user):

    payload = {
        "user_id": str(user.id),
        "tenant_id": str(user.tenant_id),
        "exp": datetime.now() + timedelta(hours=12)
    }

    token = jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return token