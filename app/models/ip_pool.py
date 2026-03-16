import uuid
from app.extensions import db
from flask_login import UserMixin

class IpPool(UserMixin, db.Model):

    __tablename__ = "ip_pools"

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    router_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("routers.id")
    )

    name = db.Column(db.String(100))

    range_start = db.Column(db.String(50))

    range_end = db.Column(db.String(50))

    router = db.relationship("Router")