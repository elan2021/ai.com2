from flask import Blueprint
from flask_restx import Api
from .auth import api_key_required

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-Key'
    }
}

api_bp = Blueprint('api', __name__, url_prefix='/api')

api = Api(
    api_bp,
    title='SaaS Platform API',
    version='1.0',
    description='A REST API for interacting with the SaaS platform.',
    authorizations=authorizations,
    security='apikey'
)

from .servicos import api as ns_servicos
from .clientes import api as ns_clientes

api.add_namespace(ns_servicos)
api.add_namespace(ns_clientes)
