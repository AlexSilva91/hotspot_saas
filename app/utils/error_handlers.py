from flask import render_template


def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(error):
        return render_template(
            "errors/generic.html",
            code=400,
            title="Requisição inválida",
            message="A requisição enviada não é válida."
        ), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return render_template(
            "errors/generic.html",
            code=401,
            title="Não autorizado",
            message="Você precisa se autenticar."
        ), 401

    @app.errorhandler(403)
    def forbidden(error):
        return render_template(
            "errors/generic.html",
            code=403,
            title="Acesso negado",
            message="Você não possui permissão para acessar este recurso."
        ), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template(
            "errors/generic.html",
            code=404,
            title="Página não encontrada",
            message="O recurso solicitado não existe."
        ), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return render_template(
            "errors/generic.html",
            code=405,
            title="Método não permitido",
            message="O método HTTP utilizado não é permitido para esta rota."
        ), 405

    @app.errorhandler(500)
    def internal_error(error):
        return render_template(
            "errors/generic.html",
            code=500,
            title="Erro interno do servidor",
            message="Ocorreu um erro inesperado no servidor."
        ), 500