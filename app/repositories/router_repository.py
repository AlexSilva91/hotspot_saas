from app.models.router import Router
from app.extensions import db
from app.middleware.tenant_middleware import tenant_filter

class RouterRepository:

    @staticmethod
    def create(data):
        router = Router(**data)
        db.session.add(router)
        db.session.commit()
        return router

    @staticmethod
    def get_all():
        query = Router.query
        query = tenant_filter(query)
        return query.all()

    @staticmethod
    def get_by_id(router_id):
        query = Router.query.filter_by(id=router_id)
        query = tenant_filter(query)
        return query.first()

    @staticmethod
    def update(router, data):
        for field, value in data.items():
            if field == "password" and not value:
                continue
            setattr(router, field, value)
        db.session.commit()
        return router

    @staticmethod
    def delete(router):
        db.session.delete(router)
        db.session.commit()