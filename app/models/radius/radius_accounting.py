import uuid
from app.extensions import db

class RadiusAccounting(db.Model):
    """Model para tabela radacct - Sessões e contabilização RADIUS"""
    __tablename__ = "radacct"

    radacctid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    nasipaddress = db.Column(db.String(15))  # IP do MikroTik
    nasportid = db.Column(db.String(50))     # Porta/interface
    acctstarttime = db.Column(db.DateTime)
    acctstoptime = db.Column(db.DateTime)
    acctsessiontime = db.Column(db.Integer)
    acctinputoctets = db.Column(db.BigInteger)
    acctoutputoctets = db.Column(db.BigInteger)
    framedipaddress = db.Column(db.String(15))
    callingstationid = db.Column(db.String(50))  # MAC do cliente
    calledstationid = db.Column(db.String(50))   # SSID ou interface
    acctterminatecause = db.Column(db.String(32))  # Motivo do término
    acctuniqueid = db.Column(db.String(32), unique=True)  # ID único da sessão
    tenant_id = db.Column(db.UUID(as_uuid=True), index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'radacctid': self.radacctid,
            'username': self.username,
            'nasipaddress': self.nasipaddress,
            'nasportid': self.nasportid,
            'acctstarttime': self.acctstarttime.isoformat() if self.acctstarttime else None,
            'acctstoptime': self.acctstoptime.isoformat() if self.acctstoptime else None,
            'acctsessiontime': self.acctsessiontime,
            'acctinputoctets': self.acctinputoctets,
            'acctoutputoctets': self.acctoutputoctets,
            'framedipaddress': self.framedipaddress,
            'callingstationid': self.callingstationid,
            'calledstationid': self.calledstationid,
            'acctterminatecause': self.acctterminatecause,
            'acctuniqueid': self.acctuniqueid,
            'tenant_id': str(self.tenant_id) if self.tenant_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @property
    def is_active(self):
        """Retorna True se a sessão ainda está ativa"""
        return self.acctstoptime is None

    @property
    def total_octets(self):
        """Total de bytes transferidos (download + upload)"""
        return (self.acctinputoctets or 0) + (self.acctoutputoctets or 0)

    def __repr__(self):
        return f'<RadiusAccounting {self.username} - {"Ativa" if self.is_active else "Encerrada"}>'