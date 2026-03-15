from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.services.hotspot_template_service import HotspotTemplateService
from app.services.tenant_service import TenantService
from app.decorators.login_required import login_required

hotspot_template_bp = Blueprint("hotspot_templates", __name__)


@hotspot_template_bp.route("/hotspot-templates", methods=["GET"])
@login_required
def list_templates():

    templates = HotspotTemplateService.list_templates()
    tenants = TenantService.list_tenants()

    return render_template(
        "hotspot_templates/list.html",
        templates=templates,
        tenants=tenants
    )


@hotspot_template_bp.route("/hotspot-templates/create", methods=["POST"])
@login_required
def create_template():

    try:

        data = {
            "tenant_id": request.form.get("tenant_id"),
            "name": request.form.get("name"),
            "login_html": request.form.get("login_html"),
            "status_html": request.form.get("status_html"),
            "logo_url": request.form.get("logo_url")
        }

        HotspotTemplateService.create_template(data)

        flash("Template criado com sucesso!", "success")

    except Exception:

        flash("Erro ao criar template!", "error")

    return redirect(url_for("hotspot_templates.list_templates"))


@hotspot_template_bp.route("/hotspot-templates/<uuid:template_id>/edit", methods=["POST"])
@login_required
def update_template(template_id):

    try:

        data = {
            "name": request.form.get("name"),
            "login_html": request.form.get("login_html"),
            "status_html": request.form.get("status_html"),
            "logo_url": request.form.get("logo_url")
        }

        HotspotTemplateService.update_template(template_id, data)

        flash("Template atualizado!", "success")

    except Exception:

        flash("Erro ao atualizar template!", "error")

    return redirect(url_for("hotspot_templates.list_templates"))


@hotspot_template_bp.route("/hotspot-templates/<uuid:template_id>/delete", methods=["POST"])
@login_required
def delete_template(template_id):

    try:

        HotspotTemplateService.delete_template(template_id)

        flash("Template removido!", "success")

    except Exception:

        flash("Erro ao remover template!", "error")

    return redirect(url_for("hotspot_templates.list_templates"))