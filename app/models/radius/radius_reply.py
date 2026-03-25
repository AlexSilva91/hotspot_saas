import uuid
from app.extensions import db

class RadiusReply(db.Model):
    """Model para tabela radreply - Atributos de resposta RADIUS"""
    __tablename__ = "radreply"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, index=True)
    attribute = db.Column(db.String(64), nullable=False)
    op = db.Column(db.String(2), nullable=False, default=":=")
    value = db.Column(db.String(255), nullable=False)
    tenant_id = db.Column(db.UUID(as_uuid=True), nullable=False, index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'attribute': self.attribute,
            'op': self.op,
            'value': self.value,
            'tenant_id': str(self.tenant_id) if self.tenant_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<RadiusReply {self.username}:{self.attribute}>'