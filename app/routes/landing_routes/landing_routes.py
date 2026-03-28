from flask import Blueprint, render_template
from app.controller.landing_controller.landing_controller import LandingController

landing_bp = Blueprint("landing", __name__)

@landing_bp.route("/")
def index():
    data = LandingController.index()
    if isinstance(data, dict):
        return render_template("dashboard/index.html", **data)
    return data

@landing_bp.route("/contato")
def contact():
    data = LandingController.contact()
    return render_template("dashboard/contact.html", **data)