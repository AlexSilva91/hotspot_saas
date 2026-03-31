# app/repositories/router_repository.py
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
    
    @classmethod
    def update_hotspot_status(cls, router_id, provisioned, config=None):
        """Método específico para atualizar status do hotspot"""
        router = cls.get_by_id(router_id)
        if router:
            router.hotspot_provisioned = provisioned
            router.hotspot_config = config
            from app.extensions import db
            db.session.commit()
            return router
        return None