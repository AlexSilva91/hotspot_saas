from functools import wraps
from flask import g
from app.models.tenant import Tenant
from app.models.user import User
from app.models.router import Router
from app.models.hotspot_user import HotspotUser


def enforce_plan_limits(resource):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            # 🔹 1. Obter tenant_id com fallback inteligente
            tenant_id = kwargs.get("tenant_id")

            # tenta pegar do data (args[0])
            if not tenant_id and args:
                data = args[0]
                if isinstance(data, dict):
                    tenant_id = data.get("tenant_id")

            # fallback para usuário logado
            if not tenant_id:
                current_user = getattr(g, "current_user", None)
                tenant_id = getattr(current_user, "tenant_id", None)

            if not tenant_id:
                return {
                    "success": False,
                    "errors": {"tenant": "Tenant não definido"}
                }

            # 🔹 2. Buscar tenant e plano
            tenant = Tenant.query.get(tenant_id)

            if not tenant or not tenant.plan:
                return {
                    "success": False,
                    "errors": {"plan": "Plano não encontrado"}
                }

            plan = tenant.plan

            # 🔹 3. Validar limites por recurso

            # USERS (usuário do sistema)
            if resource == "user":
                count = User.query.filter_by(tenant_id=tenant_id).count()

                if plan.max_users is not None and count >= plan.max_users:
                    return {
                        "success": False,
                        "errors": {
                            "max_users": f"Limite de usuários do plano atingido ({plan.max_users})"
                        }
                    }

            # ROUTERS
            elif resource == "router":
                count = Router.query.filter_by(tenant_id=tenant_id).count()

                if plan.max_routers is not None and count >= plan.max_routers:
                    return {
                        "success": False,
                        "errors": {
                            "max_routers": f"Limite de routers do plano atingido ({plan.max_routers})"
                        }
                    }

            # HOTSPOT USERS (corrigido com JOIN)
            elif resource == "hotspot_user":
                count = (
                    HotspotUser.query
                    .join(Router)
                    .filter(Router.tenant_id == tenant_id)
                    .count()
                )

                if plan.max_hotspot_users is not None and count >= plan.max_hotspot_users:
                    return {
                        "success": False,
                        "errors": {
                            "max_hotspot_users": f"Limite de hotspot users do plano atingido ({plan.max_hotspot_users})"
                        }
                    }

            # 🔹 4. Executa função original
            return func(*args, **kwargs)

        return wrapper
    return decorator