from flask import request, flash, redirect, url_for, render_template
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user
from app.repositories.user_repository import UserRepository

class AuthController:
    
    @staticmethod
    def login():
        """Login de usuário"""
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
        
        return {}  # Retorna vazio para renderizar template
    
    @staticmethod
    def logout():
        """Logout de usuário"""
        logout_user()
        flash("Você foi desconectado com sucesso.", "success")
        return redirect(url_for("auth.login"))