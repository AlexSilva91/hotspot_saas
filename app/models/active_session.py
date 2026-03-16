import uuid
from app.extensions import db
from flask_login import UserMixin

class ActiveSession(UserMixin ,db.Model):

    __tablename__ = "active_sessions"

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    router_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("routers.id")
    )

    ip_address = db.Column(db.String(50))

    mac_address = db.Column(db.String(50))

    username = db.Column(db.String(100))

    login_time = db.Column(db.DateTime)

    router = db.relationship("Router")