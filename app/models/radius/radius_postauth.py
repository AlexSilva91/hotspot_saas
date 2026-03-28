# app/models/radius/radius_postauth.py
from app.extensions import db
from sqlalchemy import Index, text
from sqlalchemy.dialects.postgresql import UUID

class RadiusPostAuth(db.Model):
    """Model para tabela radpostauth - Log de autenticações RADIUS"""
    __tablename__ = "radpostauth"
    __table_args__ = (
        Index("radpostauth_username_idx", "username"),
        Index("radpostauth_class_idx", "class"),
        Index("idx_radpostauth_tenant", "tenant_id"),
        Index("idx_radpostauth_tenant_authdate", "tenant_id", "authdate"),
        {"extend_existing": True},
    )

    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.Text, nullable=False)
    pass_ = db.Column("pass", db.Text)
    reply = db.Column(db.Text)
    calledstationid = db.Column(db.Text)
    callingstationid = db.Column(db.Text)
    authdate = db.Column(db.DateTime(timezone=True), nullable=False, server_default=text("now()"))
    class_ = db.Column("class", db.Text)
    
    # NOVO: Campo tenant_id
    tenant_id = db.Column(UUID(as_uuid=True), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'reply': self.reply,
            'authdate': self.authdate.isoformat() if self.authdate else None,
            'calledstationid': self.calledstationid,
            'callingstationid': self.callingstationid,
            'tenant_id': str(self.tenant_id) if self.tenant_id else None
        }

    def __repr__(self):
        return f"<RadiusPostAuth {self.username} - {self.reply}>"