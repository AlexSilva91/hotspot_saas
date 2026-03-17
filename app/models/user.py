import uuid
from app.extensions import db
import enum
from flask_login import UserMixin

class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    USER = "USER"
    VIEWER = "VIEWER"

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    tenant_id = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("tenants.id"),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.Enum(UserRole),
        default=UserRole.ADMIN,
        nullable=False
    )

    active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    tenant = db.relationship(
        "Tenant",
        back_populates="users"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "tenant_id",
            "email",
            name="uq_user_email_per_tenant"
        ),
    )
    
    
    def to_dict(self, include_tenant=True):
            """Retorna todas as informações do usuário"""
            return {
                'id': str(self.id) if self.id else None,
                'tenant_id': str(self.tenant_id) if self.tenant_id else None,
                'email': self.email,
                'role': self.role.value if self.role else None,
                'active': self.active,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'tenant': {
                    'id': str(self.tenant.id) if self.tenant and self.tenant.id else None,
                    'name': self.tenant.name if self.tenant and hasattr(self.tenant, 'name') else None
                } if include_tenant and self.tenant else None
            }

    @classmethod
    def get_all_info(cls, users=None):
        """Retorna informações de todos os usuários"""
        if users is None:
            users = cls.query.all()
        return [user.to_dict() for user in users]
    
    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def is_manager(self):
        return self.role == UserRole.MANAGER

    @property
    def is_staff(self):
        return self.role in {UserRole.ADMIN, UserRole.MANAGER}