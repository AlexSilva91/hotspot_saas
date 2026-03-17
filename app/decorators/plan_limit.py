from functools import wraps
from flask import g
from app.models.tenant import Tenant
from app.models.user import User
from app.models.router import Router
from app.models.hotspot_user import HotspotUser

def enforce_plan_limits(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tenant_id = kwargs.get("tenant_id") or getattr(g, "current_user", None).tenant_id
        if not tenant_id:
            return {"success": False, "errors": {"tenant": "Tenant não definido"}}
        
        tenant = Tenant.query.get(tenant_id)
        if not tenant or not tenant.plan:
            return {"success": False, "errors": {"plan": "Plano não encontrado"}}

        plan = tenant.plan
        resource_type = func.__name__

        if resource_type in ("create_user", "update_user"):
            if plan.max_users is not None and User.query.filter_by(tenant_id=tenant_id).count() >= plan.max_users:
                return {"success": False, "errors": {"max_users": f"Limite de usuários do plano atingido ({plan.max_users})"}}
        elif resource_type in ("create_router", "update_router"):
            if plan.max_routers is not None and Router.query.filter_by(tenant_id=tenant_id).count() >= plan.max_routers:
                return {"success": False, "errors": {"max_routers": f"Limite de routers do plano atingido ({plan.max_routers})"}}
        elif resource_type in ("create_hotspot_user", "update_hotspot_user"):
            if plan.max_hotspot_users is not None and HotspotUser.query.filter_by(tenant_id=tenant_id).count() >= plan.max_hotspot_users:
                return {"success": False, "errors": {"max_hotspot_users": f"Limite de hotspot users do plano atingido ({plan.max_hotspot_users})"}}

        # executa normalmente
        return func(*args, **kwargs)
    
    return wrapper