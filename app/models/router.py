# app/models/router.py
import uuid
from app.extensions import db
from flask_login import UserMixin

class Router(UserMixin, db.Model):

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
    hotspot_name = db.Column(db.String(100), default="hotspot1")
    api_port = db.Column(db.Integer, default=8728)

    username = db.Column(db.String(100))

    password = db.Column(db.String(200))

    location = db.Column(db.String(150))
    
    hotspot_provisioned = db.Column(db.Boolean, default=False)
    
    hotspot_config = db.Column(db.JSON, nullable=True)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    tenant = db.relationship(
        "Tenant",
        back_populates="routers"
    )