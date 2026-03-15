import uuid
from app.extensions import db


class HotspotUser(db.Model):

    __tablename__ = "hotspot_users"

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    router_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("routers.id")
    )

    username = db.Column(db.String(100))

    password = db.Column(db.String(100))

    limit_uptime = db.Column(db.String(50))

    rate_limit = db.Column(db.String(50))

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    router = db.relationship("Router")