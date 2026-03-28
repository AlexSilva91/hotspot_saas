# app/models/radius/radius_usergroup.py (NOVO MODEL)
from app.extensions import db
from sqlalchemy import Index, text
from sqlalchemy.dialects.postgresql import UUID

class RadiusUserGroup(db.Model):
    """Model para tabela radusergroup - Associação usuário-grupo"""
    __tablename__ = "radusergroup"
    __table_args__ = (
        Index("radusergroup_username", "username"),
        Index("idx_radusergroup_tenant", "tenant_id"),
        {"extend_existing": True},
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, server_default=text("''"))
    groupname = db.Column(db.Text, nullable=False, server_default=text("''"))
    priority = db.Column(db.Integer, nullable=False, default=1)
    
    # NOVO: Campo tenant_id
    tenant_id = db.Column(UUID(as_uuid=True), nullable=True)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'groupname': self.groupname,
            'priority': self.priority,
            'tenant_id': str(self.tenant_id) if self.tenant_id else None
        }