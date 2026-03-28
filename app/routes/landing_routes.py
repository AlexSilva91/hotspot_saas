# app/routes/landing_routes.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

landing_bp = Blueprint("landing", __name__)


@landing_bp.route("/")
def index():
    """Landing page do sistema"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))
    
    return render_template("dashboard/index.html")


@landing_bp.route("/contato")
def contact():
    """Página de contato"""
    return render_template("dashboard/contact.html")