from flask import redirect, url_for
from flask_login import current_user

class LandingController:
    
    @staticmethod
    def index():
        """Landing page do sistema"""
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.dashboard"))
        
        return {}  # Retorna vazio pois será renderizado pelo template
    
    @staticmethod
    def contact():
        """Página de contato"""
        return {}  # Retorna vazio pois será renderizado pelo template 