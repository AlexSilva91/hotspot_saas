from app.extensions import db
from app.models.tenant import Tenant
from app.middleware.tenant_middleware import tenant_filter

class TenantRepository:

    @staticmethod
    def create(data):
        tenant = Tenant(**data)
        db.session.add(tenant)
        db.session.commit()
        return tenant

    @staticmethod
    def get_all():
        query = Tenant.query.order_by(Tenant.created_at.desc())
        query = tenant_filter(query)
        return query.all()

    @staticmethod
    def get_by_id(tenant_id):
        query = Tenant.query.filter_by(id=tenant_id)
        query = tenant_filter(query)
        return query.first()

    @staticmethod
    def save(tenant):
        db.session.add(tenant)
        db.session.commit()
        return tenant

    @staticmethod
    def delete(tenant):
        db.session.delete(tenant)
        db.session.commit()