from app.models.user import User
from app.extensions import db
from app.middleware.tenant_middleware import tenant_filter

class UserRepository:

    @staticmethod
    def create(data):
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_by_email(email):
        query = User.query.filter_by(email=email)
        query = tenant_filter(query)
        return query.first()

    @staticmethod
    def get_all():
        query = User.query.order_by(User.created_at.desc())
        query = tenant_filter(query)
        return query.all()

    @staticmethod
    def get_by_tenant(tenant_id):
        query = User.query.filter_by(tenant_id=tenant_id).order_by(User.created_at.desc())
        return query.all()

    @staticmethod
    def get_by_id(user_id):
        query = User.query.filter_by(id=user_id)
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