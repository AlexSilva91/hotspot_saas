import uuid
from app.extensions import db


class Router(db.Model):

    __tablename__ = "routers"

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    tenant_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("tenants.id"),
        nullable=False
    )

    name = db.Column(db.String(100), nullable=False)

    ip_address = db.Column(db.String(50), nullable=False)

    api_port = db.Column(db.Integer, default=8728)

    username = db.Column(db.String(100))

    password = db.Column(db.String(200))

    location = db.Column(db.String(150))

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    tenant = db.relationship(
        "Tenant",
        back_populates="routers"
    )