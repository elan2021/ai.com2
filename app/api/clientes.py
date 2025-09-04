from flask import g, request
from flask_restx import Namespace, Resource, fields
from ..models import Cliente
from .auth import api_key_required
from .. import db

api = Namespace('clientes', description='Operações relacionadas a clientes')

cliente_model = api.model('Cliente', {
    'id': fields.Integer(readonly=True, description='O identificador único do cliente'),
    'nome': fields.String(required=True, description='O nome do cliente'),
    'telefone': fields.String(required=True, description='O telefone de contato do cliente'),
})

# Parser para os dados de entrada do novo cliente
cliente_parser = api.parser()
cliente_parser.add_argument('nome', type=str, required=True, help='Nome do cliente', location='json')
cliente_parser.add_argument('telefone', type=str, required=True, help='Telefone do cliente', location='json')

@api.route('/')
class ClienteList(Resource):
    @api.doc(security='apikey')
    @api.expect(cliente_parser)
    @api.marshal_with(cliente_model, code=201)
    @api_key_required
    def post(self):
        """Cria um novo cliente"""
        args = cliente_parser.parse_args()
        loja = g.loja

        novo_cliente = Cliente(
            nome=args['nome'],
            telefone=args['telefone'],
            loja_id=loja.id
        )
        db.session.add(novo_cliente)
        db.session.commit()
        return novo_cliente, 201
