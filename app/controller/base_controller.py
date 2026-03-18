from flask import flash, redirect, url_for, session


class BaseController:

    @staticmethod
    def handle_result(result, success_message, error_default="Erro na operação", 
                      redirect_to=None, form_data=None):
        """
        Padroniza:
        - flash automático
        - redirect
        - tratamento de erros
        - salvamento de dados do formulário em caso de erro
        """

        if result.get("success"):
            flash(success_message, "success")
        else:
            errors = result.get("errors", {})
            if errors:
                for msg in errors.values():
                    flash(msg, "error")
            else:
                flash(error_default, "error")
            
            # Salva dados do formulário em caso de erro
            if form_data:
                session["form_data"] = form_data
                session["form_errors"] = errors

        if redirect_to:
            return redirect(url_for(redirect_to))

        return result  # fallback (caso queira usar sem redirect)