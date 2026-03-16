from app.models.ip_pool import IpPool
from app.models.router import Router
from app.extensions import db
from app.middleware.tenant_middleware import tenant_filter

class IpPoolRepository:

    @staticmethod
    def create(data):
        ip_pool = IpPool(**data)
        db.session.add(ip_pool)
        db.session.commit()
        return ip_pool

    @staticmethod
    def get_all():
        query = IpPool.query.join(Router)
        query = tenant_filter(query)
        return query.all()

    @staticmethod
    def get_by_id(pool_id):
        query = IpPool.query.join(Router).filter(IpPool.id == pool_id)
        query = tenant_filter(query)
        return query.first()

    @staticmethod
    def save(pool):
        db.session.add(pool)
        db.session.commit()
        return pool

    @staticmethod
    def delete(pool):
        db.session.delete(pool)
        db.session.commit()