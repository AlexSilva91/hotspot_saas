import uuid
from app.extensions import db


class HotspotTemplate(db.Model):

    __tablename__ = "hotspot_templates"

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    tenant_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("tenants.id")
    )

    name = db.Column(db.String(100))

    login_html = db.Column(db.Text)

    status_html = db.Column(db.Text)

    logo_url = db.Column(db.String(200))

    tenant = db.relationship("Tenant")