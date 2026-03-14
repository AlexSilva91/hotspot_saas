import uuid
from app.extensions import db


class Tenant(db.Model):

    __tablename__ = "tenants"

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = db.Column(
        db.String(120),
        nullable=False
    )

    plan_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("plans.id")
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    plan = db.relationship(
        "Plan",
        lazy="joined"
    )

    users = db.relationship(
        "User",
        back_populates="tenant"
    )