from flask import Blueprint, render_template
from flask_login import login_required
from app.controller.dashboard_controller.dashboard_controller import DashboardController

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    data = DashboardController.dashboard()
    return render_template("dashboard/dashboard.html", **data)