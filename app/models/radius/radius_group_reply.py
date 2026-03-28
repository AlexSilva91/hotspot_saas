# app/models/radius/radius_group_reply.py (NOVO MODEL)
from app.extensions import db
from sqlalchemy import Index, text
from sqlalchemy.dialects.postgresql import UUID

class RadiusGroupReply(db.Model):
    """Model para tabela radgroupreply - Atributos de grupo RADIUS"""
    __tablename__ = "radgroupreply"
    __table_args__ = (
        Index("radgroupreply_groupname", "groupname", "attribute"),
        Index("idx_radgroupreply_tenant", "tenant_id"),
        {"extend_existing": True},
    )

    id = db.Column(db.Integer, primary_key=True)
    groupname = db.Column(db.Text, nullable=False, server_default=text("''"))
    attribute = db.Column(db.Text, nullable=False, server_default=text("''"))
    op = db.Column(db.String(2), nullable=False, server_default=text("'='::character varying"))
    value = db.Column(db.Text, nullable=False, server_default=text("''"))
    
    # NOVO: Campo tenant_id
    tenant_id = db.Column(UUID(as_uuid=True), nullable=True)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'groupname': self.groupname,
            'attribute': self.attribute,
            'op': self.op,
            'value': self.value,
            'tenant_id': str(self.tenant_id) if self.tenant_id else None
        }