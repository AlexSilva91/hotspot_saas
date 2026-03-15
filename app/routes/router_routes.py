from flask import Blueprint, flash, request, render_template, redirect, url_for
from app.services.router_service import RouterService
from app.services.tenant_service import TenantService
from app.extensions import db
from app.decorators.login_required import login_required

router_bp = Blueprint("routers", __name__)


# LISTAR
@router_bp.route("/routers", methods=["GET"])
@login_required
def list_routers():

    routers = RouterService.list_routers()
    tenants = TenantService.list_tenants()

    return render_template(
        "routers/list.html",
        routers=routers,
        tenants=tenants
    )


# CRIAR
@router_bp.route("/routers/create", methods=["POST"])
@login_required
def create_router():
    try:
        data = {
            "name": request.form.get("name"),
            "ip_address": request.form.get("ip_address"),
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "tenant_id": request.form.get("tenant_id")
        }

        RouterService.create_router(data)
        flash('Roteador cadastrado com sucesso!', 'success')
    except Exception as e:
        flash('Não foi possível cadastrar roteador!', 'error')

    return redirect(url_for("routers.list_routers"))


# PAGINA EDITAR
@router_bp.route("/routers/<uuid:router_id>/edit", methods=["GET"])
@login_required
def edit_router_page(router_id):

    router = RouterService.get_router(router_id)
    tenants = TenantService.list_tenants()

    return render_template(
        "routers/edit.html",
        router=router,
        tenants=tenants
    )


# ATUALIZAR
@router_bp.route("/routers/<uuid:router_id>/edit", methods=["POST"])
@login_required
def update_router(router_id):
    try:
        router = RouterService.get_router(router_id)

        router.name = request.form.get("name")
        router.ip_address = request.form.get("ip_address")
        router.username = request.form.get("username")

        password = request.form.get("password")
        if password:
            router.password = password

        router.tenant_id = request.form.get("tenant_id")

        db.session.commit()
        flash('Roteador atualizado com sucesso!', 'success')
    except Exception as e:
        flash('Não foi possível atualizar roteador!', 'error')
        
    return redirect(url_for("routers.list_routers"))


# REMOVER
@router_bp.route("/routers/<uuid:router_id>/delete", methods=["POST"])
@login_required
def delete_router(router_id):
    try:
        RouterService.delete_router(router_id)
    
        flash('Roteador removido com sucesso!', 'success')
    except Exception as e:
        flash('Não foi possível remover roteador!', 'error')

    return redirect(url_for("routers.list_routers"))