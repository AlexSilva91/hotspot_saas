from flask import Blueprint, abort

error_test_bp = Blueprint("error_test", __name__)


@error_test_bp.route("/test/400")
def test_400():
    abort(400)


@error_test_bp.route("/test/401")
def test_401():
    abort(401)


@error_test_bp.route("/test/403")
def test_403():
    abort(403)


@error_test_bp.route("/test/404")
def test_404():
    abort(404)


@error_test_bp.route("/test/405", methods=["GET"])
def test_405():
    abort(405)


@error_test_bp.route("/test/500")
def test_500():
    raise Exception("Erro interno de teste")