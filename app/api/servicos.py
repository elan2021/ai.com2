from flask import g
from flask_restx import Namespace, Resource, fields
from ..models import Servico
from .auth import api_key_required

api = Namespace('servicos', description='Operações relacionadas a serviços')

# Modelo aninhado para o profissional
profissional_servico_model = api.model('ProfissionalServico', {
    'id': fields.Integer(readonly=True, description='O ID do profissional'),
    'nome': fields.String(readonly=True, attribute='user.nome', description='O nome do profissional'),
})

servico_model = api.model('Servico', {
    'id': fields.Integer(readonly=True, description='O identificador único do serviço'),
    'nome': fields.String(required=True, description='O nome do serviço'),
    'duracao': fields.Integer(required=True, description='A duração do serviço em minutos'),
    'preco': fields.Float(required=True, description='O preço do serviço'),
    'profissionais': fields.List(fields.Nested(profissional_servico_model), readonly=True, description='Lista de profissionais que realizam o serviço'),
})

@api.route('/')
class ServicoList(Resource):
    @api.doc(security='apikey')
    @api.marshal_list_with(servico_model)
    @api_key_required
    def get(self):
        """Lista todos os serviços da loja"""
        loja = g.loja
        return loja.servicos, 200
