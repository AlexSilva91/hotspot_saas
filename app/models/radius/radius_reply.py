from app.extensions import db
from sqlalchemy import Index, text

class RadiusReply(db.Model):
    """Model para tabela radreply - Atributos de resposta RADIUS"""
    __tablename__ = "radreply"
    __table_args__ = (
        Index("radreply_username", "username", "attribute"),
        {"extend_existing": True},
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, server_default=text("''"))
    attribute = db.Column(db.Text, nullable=False, server_default=text("''"))
    op = db.Column(db.String(2), nullable=False, server_default=text("'='::character varying"))
    value = db.Column(db.Text, nullable=False, server_default=text("''"))

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