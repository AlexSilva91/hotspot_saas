import uuid
from app.extensions import db


class Plan(db.Model):

    __tablename__ = "plans"

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = db.Column(db.String(100), nullable=False)

    max_routers = db.Column(db.Integer, default=1)

    max_users = db.Column(db.Integer, default=5)

    max_hotspot_users = db.Column(db.Integer, default=500)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )