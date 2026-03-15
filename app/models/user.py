import uuid
from app.extensions import db


class User(db.Model):

    __tablename__ = "users"

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

    email = db.Column(
        db.String(120),
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(50),
        default="admin"
    )

    active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    tenant = db.relationship(
        "Tenant",
        back_populates="users"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "tenant_id",
            "email",
            name="uq_user_email_per_tenant"
        ),
    )