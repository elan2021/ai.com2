from flask import g, request
from flask_restx import Namespace, Resource, reqparse
from sqlalchemy import func
from ..models import Profissional, Servico, HorarioTrabalho, Agendamento
from .auth import api_key_required
from datetime import datetime, time, timedelta

api = Namespace('disponibilidade', description='Operações relacionadas à disponibilidade de horários')

parser = reqparse.RequestParser()
parser.add_argument('profissional_id', type=int, required=True, help='ID do profissional')
parser.add_argument('servico_id', type=int, required=True, help='ID do serviço')
parser.add_argument('data', type=str, required=True, help='Data para verificar a disponibilidade (YYYY-MM-DD)')

@api.route('/')
@api.doc(parser=parser)
class Disponibilidade(Resource):
    @api.doc(security='apikey')
    @api_key_required
    def get(self):
        """Verifica horários disponíveis para um profissional/serviço em uma data"""
        args = parser.parse_args()
        loja = g.loja

        try:
            data_desejada = datetime.strptime(args['data'], '%Y-%m-%d').date()
        except ValueError:
            api.abort(400, "Formato de data inválido. Use YYYY-MM-DD.")

        profissional = Profissional.query.filter_by(id=args['profissional_id'], loja_id=loja.id).first_or_404('Profissional não encontrado.')
        servico = Servico.query.filter_by(id=args['servico_id'], loja_id=loja.id).first_or_404('Serviço não encontrado.')

        dia_da_semana = data_desejada.weekday() # Segunda: 0, Domingo: 6
        horario_trabalho = HorarioTrabalho.query.filter_by(profissional_id=profissional.id, dia_da_semana=dia_da_semana).first()

        if not horario_trabalho or horario_trabalho.e_folga:
            return {'horarios_disponiveis': []}, 200

        # Montar blocos de tempo ocupados
        blocos_ocupados = []
        # Almoço
        if horario_trabalho.almoco_inicio and horario_trabalho.almoco_fim:
            blocos_ocupados.append((horario_trabalho.almoco_inicio, horario_trabalho.almoco_fim))

        # Agendamentos existentes
        start_of_day = datetime.combine(data_desejada, time.min)
        end_of_day = datetime.combine(data_desejada, time.max)
        agendamentos_do_dia = Agendamento.query.filter(
            Agendamento.profissional_id == profissional.id,
            Agendamento.data_hora_inicio.between(start_of_day, end_of_day)
        ).all()

        for ag in agendamentos_do_dia:
            blocos_ocupados.append((ag.data_hora_inicio.time(), ag.data_hora_fim.time()))

        # Lógica para encontrar horários vagos
        horarios_disponiveis = []
        duracao_total = timedelta(minutes=servico.duracao + (horario_trabalho.pausa_entre_atendimentos or 0))

        slot_atual = datetime.combine(data_desejada, horario_trabalho.horario_inicio)
        fim_do_dia = datetime.combine(data_desejada, horario_trabalho.horario_fim)

        while slot_atual + timedelta(minutes=servico.duracao) <= fim_do_dia:
            slot_fim = slot_atual + timedelta(minutes=servico.duracao)

            # Checar se o slot está dentro de algum bloco ocupado
            ocupado = False
            for inicio_ocupado, fim_ocupado in blocos_ocupados:
                inicio_ocupado_dt = datetime.combine(data_desejada, inicio_ocupado)
                fim_ocupado_dt = datetime.combine(data_desejada, fim_ocupado)
                if max(slot_atual, inicio_ocupado_dt) < min(slot_fim, fim_ocupado_dt):
                    ocupado = True
                    break

            if not ocupado:
                horarios_disponiveis.append(slot_atual.strftime('%H:%M'))

            # Próximo slot considera a pausa
            slot_atual += duracao_total
            # Para evitar loop infinito se a duração for 0
            if duracao_total.total_seconds() == 0:
                break

        return {'horarios_disponiveis': horarios_disponiveis}, 200
