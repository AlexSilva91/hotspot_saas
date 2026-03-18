from app.models.user import User
from app.repositories.base_repository import BaseRepository
from app.middleware.tenant_middleware import tenant_filter

class UserRepository(BaseRepository):
    model = User

    @classmethod
    def get_all(cls):
        query = cls.model.query.order_by(User.created_at.desc())
        query = tenant_filter(query)
        return query.all()

    @classmethod
    def get_by_email(cls, email):
        query = cls.model.query.filter_by(email=email)
        query = tenant_filter(query)
        return query.first()

    @classmethod
    def get_by_tenant(cls, tenant_id):
        query = cls.model.query.filter_by(tenant_id=tenant_id).order_by(User.created_at.desc())
        return query.all()