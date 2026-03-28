# app/models/radius/radius_accounting.py
from app.extensions import db
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy import Index, text

class RadiusAccounting(db.Model):
    """Model para tabela radacct - Sessões e contabilização RADIUS"""
    __tablename__ = "radacct"
    __table_args__ = (
        Index("radacct_active_session_idx", "acctuniqueid", 
              postgresql_where=text("acctstoptime IS NULL")),
        Index("radacct_bulk_close", "nasipaddress", "acctstarttime", 
              postgresql_where=text("acctstoptime IS NULL")),
        Index("radacct_calss_idx", "class"),
        Index("radacct_start_user_idx", "acctstarttime", "username"),
        Index("idx_radacct_tenant", "tenant_id"),
        Index("idx_radacct_tenant_active", "tenant_id", 
              postgresql_where=text("acctstoptime IS NULL")),
        {"extend_existing": True},
    )

    radacctid = db.Column(db.BigInteger, primary_key=True)
    acctsessionid = db.Column(db.Text, nullable=False)
    acctuniqueid = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text)
    realm = db.Column(db.Text)
    nasipaddress = db.Column(INET, nullable=False)
    nasportid = db.Column(db.Text)
    nasporttype = db.Column(db.Text)
    acctstarttime = db.Column(db.DateTime(timezone=True))
    acctupdatetime = db.Column(db.DateTime(timezone=True))
    acctstoptime = db.Column(db.DateTime(timezone=True))
    acctinterval = db.Column(db.BigInteger)
    acctsessiontime = db.Column(db.BigInteger)
    acctauthentic = db.Column(db.Text)
    connectinfo_start = db.Column(db.Text)
    connectinfo_stop = db.Column(db.Text)
    acctinputoctets = db.Column(db.BigInteger)
    acctoutputoctets = db.Column(db.BigInteger)
    calledstationid = db.Column(db.Text)
    callingstationid = db.Column(db.Text)
    acctterminatecause = db.Column(db.Text)
    servicetype = db.Column(db.Text)
    framedprotocol = db.Column(db.Text)
    framedipaddress = db.Column(INET)
    framedipv6address = db.Column(INET)
    framedipv6prefix = db.Column(INET)
    framedinterfaceid = db.Column(db.Text)
    delegatedipv6prefix = db.Column(INET)
    class_ = db.Column("class", db.Text)
    
    # NOVO: Campo tenant_id
    tenant_id = db.Column(UUID(as_uuid=True), nullable=False)

    @property
    def is_active(self):
        return self.acctstoptime is None

    @property
    def total_octets(self):
        return (self.acctinputoctets or 0) + (self.acctoutputoctets or 0)

    @property
    def total_mb(self):
        return self.total_octets / (1024 * 1024)

    def to_dict(self):
        return {
            'radacctid': self.radacctid,
            'acctsessionid': self.acctsessionid,
            'acctuniqueid': self.acctuniqueid,
            'username': self.username,
            'nasipaddress': str(self.nasipaddress) if self.nasipaddress else None,
            'acctstarttime': self.acctstarttime.isoformat() if self.acctstarttime else None,
            'acctstoptime': self.acctstoptime.isoformat() if self.acctstoptime else None,
            'acctsessiontime': self.acctsessiontime,
            'acctinputoctets': self.acctinputoctets,
            'acctoutputoctets': self.acctoutputoctets,
            'framedipaddress': str(self.framedipaddress) if self.framedipaddress else None,
            'callingstationid': self.callingstationid,
            'calledstationid': self.calledstationid,
            'acctterminatecause': self.acctterminatecause,
            'is_active': self.is_active,
            'total_mb': self.total_mb,
            'tenant_id': str(self.tenant_id) if self.tenant_id else None
        }

    def __repr__(self):
        return f"<RadiusAccounting {self.username} - {'Ativa' if self.is_active else 'Encerrada'}>"