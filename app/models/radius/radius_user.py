# app/models/radius/radius_user.py
from app.extensions import db
from sqlalchemy import Index, text
from sqlalchemy.dialects.postgresql import UUID
import uuid

class RadiusUser(db.Model):
    """Model para tabela radcheck - Autenticação RADIUS"""
    __tablename__ = "radcheck"
    __table_args__ = (
        Index("radcheck_username", "username", "attribute"),
        Index("idx_radcheck_tenant", "tenant_id"),
        Index("idx_radcheck_tenant_username", "tenant_id", "username"),
        {"extend_existing": True},
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, server_default=text("''"))
    attribute = db.Column(db.Text, nullable=False, server_default=text("''"))
    op = db.Column(db.String(2), nullable=False, server_default=text("'=='::character varying"))
    value = db.Column(db.Text, nullable=False, server_default=text("''"))
    
    # NOVO: Campo tenant_id para isolamento multi-tenant
    tenant_id = db.Column(UUID(as_uuid=True), nullable=False)
    
    # Campos de auditoria
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    created_by = db.Column(UUID(as_uuid=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'attribute': self.attribute,
            'op': self.op,
            'value': self.value,
            'tenant_id': str(self.tenant_id) if self.tenant_id else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<RadiusUser {self.username}>"