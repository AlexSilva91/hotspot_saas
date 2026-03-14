from app.extensions import db
import uuid

class Plan(db.Model):

    __tablename__ = "plans"

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = db.Column(db.String(100))

    max_routers = db.Column(db.Integer)

    max_users = db.Column(db.Integer)