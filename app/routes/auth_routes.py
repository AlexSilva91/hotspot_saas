from flask import Blueprint, request, render_template, redirect, url_for, flash
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required
from app.repositories.user_repository import UserRepository

auth_bp = Blueprint("auth", __name__)


# ------------------- LOGIN -------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = UserRepository.get_by_email(email)

        if not user or not check_password_hash(user.password_hash, password):
            flash("Credenciais inválidas", "error")
            return redirect(url_for("auth.login"))

        login_user(user)

        flash(f"Bem-vindo, {user.email}!", "success")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("auth/login.html")


# ------------------- LOGOUT -------------------
@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Você foi desconectado com sucesso.", "success")

    return redirect(url_for("auth.login"))