from flask import g
from app.models.router import Router
from app.models.tenant import Tenant
from app.models.plan import Plan


def check_router_limit():

    tenant = Tenant.query.get(g.tenant_id)

    plan = Plan.query.get(tenant.plan_id)

    if plan.max_routers is None:
        return True

    router_count = Router.query.filter_by(
        tenant_id=g.tenant_id
    ).count()

    if router_count >= plan.max_routers:
        raise Exception("Limite de routers do plano atingido")

    return True