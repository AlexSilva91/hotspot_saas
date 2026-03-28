from flask import abort

class ErrorTestController:
    
    @staticmethod
    def test_400():
        abort(400)
    
    @staticmethod
    def test_401():
        abort(401)
    
    @staticmethod
    def test_403():
        abort(403)
    
    @staticmethod
    def test_404():
        abort(404)
    
    @staticmethod
    def test_405():
        abort(405)
    
    @staticmethod
    def test_500():
        raise Exception("Erro interno de teste")