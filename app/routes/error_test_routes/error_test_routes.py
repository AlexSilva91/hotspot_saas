from flask import Blueprint
from app.controller.error_test_controller.error_test_controller import ErrorTestController

error_test_bp = Blueprint("error_test", __name__)

@error_test_bp.route("/test/400")
def test_400():
    return ErrorTestController.test_400()

@error_test_bp.route("/test/401")
def test_401():
    return ErrorTestController.test_401()

@error_test_bp.route("/test/403")
def test_403():
    return ErrorTestController.test_403()

@error_test_bp.route("/test/404")
def test_404():
    return ErrorTestController.test_404()

@error_test_bp.route("/test/405", methods=["GET"])
def test_405():
    return ErrorTestController.test_405()

@error_test_bp.route("/test/500")
def test_500():
    return ErrorTestController.test_500()