# app/models/radius/radius_reply.py
from app.extensions import db
from sqlalchemy import Index, text
from sqlalchemy.dialects.postgresql import UUID

class RadiusReply(db.Model):
    """Model para tabela radreply - Atributos de resposta RADIUS"""
    __tablename__ = "radreply"
    __table_args__ = (
        Index("radreply_username", "username", "attribute"),
        Index("idx_radreply_tenant", "tenant_id"),
        Index("idx_radreply_tenant_username", "tenant_id", "username"),
        {"extend_existing": True},
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, server_default=text("''"))
    attribute = db.Column(db.Text, nullable=False, server_default=text("''"))
    op = db.Column(db.String(2), nullable=False, server_default=text("'='::character varying"))
    value = db.Column(db.Text, nullable=False, server_default=text("''"))
    
    tenant_id = db.Column(UUID(as_uuid=True), nullable=True)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'attribute': self.attribute,
            'op': self.op,
            'value': self.value,
            'tenant_id': str(self.tenant_id) if self.tenant_id else None
        }

    def __repr__(self):
        return f"<RadiusReply {self.username}:{self.attribute}>"