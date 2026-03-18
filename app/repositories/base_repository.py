from app.extensions import db
from app.middleware.tenant_middleware import tenant_filter

class BaseRepository:
    model = None

    @classmethod
    def create(cls, data):
        obj = cls.model(**data)
        db.session.add(obj)
        db.session.commit()
        return obj

    @classmethod
    def get_all(cls):
        query = cls.model.query
        query = tenant_filter(query)
        return query.all()

    @classmethod
    def get_by_id(cls, obj_id):
        query = cls.model.query.filter_by(id=obj_id)
        query = tenant_filter(query)
        return query.first()

    @classmethod
    def update(cls, obj, data):
        for field, value in data.items():
            setattr(obj, field, value)
        db.session.commit()
        return obj

    @classmethod
    def delete(cls, obj):
        db.session.delete(obj)
        db.session.commit()