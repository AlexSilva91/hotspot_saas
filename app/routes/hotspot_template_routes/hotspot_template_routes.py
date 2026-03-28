from flask import Blueprint, render_template
from flask_login import login_required
from app.controller.hotspot_template_controller.hotspot_template_controller import HotspotTemplateController

hotspot_template_bp = Blueprint("hotspot_templates", __name__)

@hotspot_template_bp.route("/hotspot-templates", methods=["GET"])
@login_required
def list_templates():
    data = HotspotTemplateController.list()
    return render_template("hotspot_templates/list.html", **data)

@hotspot_template_bp.route("/hotspot-templates/create", methods=["POST"])
@login_required
def create_template():
    return HotspotTemplateController.create()

@hotspot_template_bp.route("/hotspot-templates/<uuid:template_id>/edit", methods=["POST"])
@login_required
def update_template(template_id):
    return HotspotTemplateController.update(template_id)

@hotspot_template_bp.route("/hotspot-templates/<uuid:template_id>/delete", methods=["POST"])
@login_required
def delete_template(template_id):
    return HotspotTemplateController.delete(template_id)