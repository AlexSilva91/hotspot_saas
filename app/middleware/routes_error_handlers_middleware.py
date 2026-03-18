from flask import jsonify, flash, redirect, url_for


def register_error_handlers_routes(app):

    @app.errorhandler(Exception)
    def handle_exception(e):
        # log aqui se quiser
        print(f"[ERROR] {str(e)}")

        # resposta API (se for JSON)
        if "application/json" in str(e):
            return jsonify({
                "success": False,
                "errors": {"internal": "Erro interno do servidor"}
            }), 500

        # resposta web (flash + redirect fallback)
        flash("Erro interno inesperado", "error")
        return redirect(url_for("dashboard.dashboard"))