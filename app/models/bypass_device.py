import uuid
from app.extensions import db
from flask_login import UserMixin

class BypassDevice(UserMixin, db.Model):

    __tablename__ = "bypass_devices"

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    router_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("routers.id")
    )

    mac_address = db.Column(db.String(50))

    comment = db.Column(db.String(200))

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    router = db.relationship("Router")