from app.models.hotspot_user import HotspotUser
from app.models.router import Router
from app.extensions import db
from app.middleware.tenant_middleware import tenant_filter

class HotspotUserRepository:

    @staticmethod
    def create(data):
        user = HotspotUser(**data)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_all():
        query = HotspotUser.query.join(Router)
        query = tenant_filter(query)
        return query.all()

    @staticmethod
    def get_by_id(user_id):
        query = HotspotUser.query.join(Router).filter(HotspotUser.id == user_id)
        query = tenant_filter(query)
        return query.first()

    @staticmethod
    def save(user):
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def delete(user):
        db.session.delete(user)
        db.session.commit()