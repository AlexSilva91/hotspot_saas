import uuid
from app.extensions import db

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey("tenants.id"))

    email = db.Column(db.String(120), unique=True)

    password_hash = db.Column(db.String)

    role = db.Column(db.String(50))