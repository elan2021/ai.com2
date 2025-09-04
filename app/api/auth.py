from functools import wraps
from flask import request, g, abort
from app.models import Loja

def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            abort(401, description="API key is missing.")

        loja = Loja.query.filter_by(api_key=api_key).first()
        if not loja:
            abort(401, description="API key is invalid.")

        g.loja = loja  # Armazena a loja no contexto da requisição
        return f(*args, **kwargs)
    return decorated_function
