import uuid
from app.extensions import db

class Router(db.Model):

    __tablename__ = "routers"

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey("tenants.id"))

    name = db.Column(db.String(100))

    ip_address = db.Column(db.String(50))

    username = db.Column(db.String(100))

    password = db.Column(db.String(200))