from app.models.router import Router
from app.repositories.base_repository import BaseRepository
from app.middleware.tenant_middleware import tenant_filter

class RouterRepository(BaseRepository):
    model = Router

    @classmethod
    def update(cls, obj, data):
        for field, value in data.items():
            if field == "password" and not value:
                continue
            setattr(obj, field, value)
        from app.extensions import db
        db.session.commit()
        return obj