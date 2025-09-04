from flask_restx import Namespace, Resource, fields
from ..models import Agendamento, Cliente, Profissional, Servico
from .auth import api_key_required
from .. import db
from flask import g, request
from datetime import datetime, timedelta

api = Namespace('agendamentos', description='Operações relacionadas a agendamentos')

# --- Modelos para Marshalling (Saída) ---
servico_agendamento_model = api.model('ServicoAgendamento', {
    'id': fields.Integer(),
    'nome': fields.String(),
})

profissional_agendamento_model = api.model('ProfissionalAgendamento', {
    'id': fields.Integer(),
    'nome': fields.String(attribute='user.nome'),
})

cliente_agendamento_model = api.model('ClienteAgendamento', {
    'id': fields.Integer(),
    'nome': fields.String(),
})

agendamento_model = api.model('Agendamento', {
    'id': fields.Integer(readonly=True),
    'data_hora_inicio': fields.DateTime,
    'data_hora_fim': fields.DateTime,
    'status': fields.String,
    'cliente': fields.Nested(cliente_agendamento_model),
    'profissional': fields.Nested(profissional_agendamento_model),
    'servico': fields.Nested(servico_agendamento_model),
})

# --- Parsers para Validação (Entrada) ---
agendamento_post_parser = api.parser()
agendamento_post_parser.add_argument('cliente_id', type=int, required=True, help='ID do Cliente', location='json')
agendamento_post_parser.add_argument('profissional_id', type=int, required=True, help='ID do Profissional', location='json')
agendamento_post_parser.add_argument('servico_id', type=int, required=True, help='ID do Serviço', location='json')
agendamento_post_parser.add_argument('data', type=str, required=True, help='Data do agendamento (YYYY-MM-DD)', location='json')
agendamento_post_parser.add_argument('hora_inicio', type=str, required=True, help='Hora de início do agendamento (HH:MM)', location='json')

agendamento_put_parser = api.parser()
agendamento_put_parser.add_argument('status', type=str, required=True, choices=('confirmado', 'cancelado'), help='Novo status do agendamento', location='json')


@api.route('/')
class AgendamentoList(Resource):
    @api.doc(security='apikey')
    @api.expect(agendamento_post_parser)
    @api.marshal_with(agendamento_model, code=201)
    @api_key_required
    def post(self):
        """Cria um novo agendamento"""
        args = agendamento_post_parser.parse_args()
        loja = g.loja

        # Validação
        cliente = Cliente.query.filter_by(id=args['cliente_id'], loja_id=loja.id).first_or_404(description='Cliente não encontrado ou não pertence a esta loja.')
        profissional = Profissional.query.filter_by(id=args['profissional_id'], loja_id=loja.id).first_or_404(description='Profissional não encontrado ou não pertence a esta loja.')
        servico = Servico.query.filter_by(id=args['servico_id'], loja_id=loja.id).first_or_404(description='Serviço não encontrado ou não pertence a esta loja.')

        if servico not in profissional.servicos:
            api.abort(400, 'Este profissional não realiza o serviço selecionado.')

        # Lógica de criação
        try:
            inicio = datetime.strptime(f"{args['data']} {args['hora_inicio']}", '%Y-%m-%d %H:%M')
        except ValueError:
            api.abort(400, "Formato de data ou hora inválido. Use YYYY-MM-DD e HH:MM.")

        fim = inicio + timedelta(minutes=servico.duracao)

        novo_agendamento = Agendamento(
            data_hora_inicio=inicio,
            data_hora_fim=fim,
            loja_id=loja.id,
            cliente_id=cliente.id,
            servico_id=servico.id,
            profissional_id=profissional.id,
            status='confirmado' # API cria agendamentos como 'confirmado'
        )
        db.session.add(novo_agendamento)
        db.session.commit()
        return novo_agendamento, 201

@api.route('/<int:id>')
class AgendamentoResource(Resource):
    @api.doc(security='apikey')
    @api.expect(agendamento_put_parser)
    @api.marshal_with(agendamento_model)
    @api_key_required
    def put(self, id):
        """Atualiza o status de um agendamento (Confirmado ou Cancelado)"""
        args = agendamento_put_parser.parse_args()
        loja = g.loja

        agendamento = Agendamento.query.get_or_404(id)
        if agendamento.loja_id != loja.id:
            api.abort(403, 'Este agendamento não pertence à sua loja.')

        agendamento.status = args['status']
        db.session.commit()
        return agendamento, 200
