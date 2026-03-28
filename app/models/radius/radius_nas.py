# app/models/radius/radius_nas.py (NOVO MODEL)
from app.extensions import db
from sqlalchemy import Index, text
from sqlalchemy.dialects.postgresql import INET, UUID

class RadiusNas(db.Model):
    """Model para tabela nas - Clientes RADIUS (MikroTiks)"""
    __tablename__ = "nas"
    __table_args__ = (
        Index("nas_nasname", "nasname"),
        Index("idx_nas_tenant", "tenant_id"),
        {"extend_existing": True},
    )

    id = db.Column(db.Integer, primary_key=True)
    nasname = db.Column(db.Text, nullable=False)
    shortname = db.Column(db.Text, nullable=False)
    type = db.Column(db.Text, nullable=False, server_default=text("'other'"))
    ports = db.Column(db.Integer)
    secret = db.Column(db.Text, nullable=False)
    server = db.Column(db.Text)
    community = db.Column(db.Text)
    description = db.Column(db.Text)
    
    # NOVO: Campo tenant_id
    tenant_id = db.Column(UUID(as_uuid=True), nullable=False)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'nasname': self.nasname,
            'shortname': self.shortname,
            'type': self.type,
            'ports': self.ports,
            'secret': self.secret,
            'server': self.server,
            'community': self.community,
            'description': self.description,
            'tenant_id': str(self.tenant_id) if self.tenant_id else None
        }