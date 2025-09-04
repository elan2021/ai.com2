from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from .models import Agendamento, Comissao, Servico
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

from . import db

@dashboard_bp.route('/')
@login_required
def index():
    if not current_user.owned_lojas:
        return redirect(url_for('loja.criar_loja'))

    loja = current_user.owned_lojas[0]
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # 1. Receita
    def get_revenue(days):
        start_date = today_start - timedelta(days=days-1)
        revenue = db.session.query(func.sum(Servico.preco)).join(Agendamento).filter(
            Agendamento.loja_id == loja.id,
            Agendamento.status == 'concluido',
            Agendamento.data_hora_inicio >= start_date
        ).scalar()
        return revenue or 0

    receita_hoje = get_revenue(1)
    receita_7_dias = get_revenue(7)
    receita_15_dias = get_revenue(15)
    receita_mes = get_revenue(30) # Simplificação para 30 dias

    # 2. Totais de Agendamento
    agendamentos_concluidos = Agendamento.query.filter_by(loja_id=loja.id, status='concluido').count()
    agendamentos_pendentes = Agendamento.query.filter_by(loja_id=loja.id, status='agendado').count()
    agendamentos_cancelados = Agendamento.query.filter_by(loja_id=loja.id, status='cancelado').count()

    # 3. Totais de Comissão
    comissoes_pendentes = db.session.query(func.sum(Comissao.valor)).filter(
        Comissao.profissional.has(loja_id=loja.id),
        Comissao.status == 'pendente'
    ).scalar() or 0
    comissoes_pagas = db.session.query(func.sum(Comissao.valor)).filter(
        Comissao.profissional.has(loja_id=loja.id),
        Comissao.status == 'paga'
    ).scalar() or 0

    # 4. Top Profissionais (Lucro = Receita - Comissão Paga)
    # Esta é uma query mais complexa, faremos uma aproximação em Python por simplicidade
    profissionais_lucro = []
    for prof in loja.profissionais:
        receita_prof = db.session.query(func.sum(Servico.preco)).join(Agendamento).filter(
            Agendamento.profissional_id == prof.id,
            Agendamento.status == 'concluido'
        ).scalar() or 0

        comissao_total_prof = db.session.query(func.sum(Comissao.valor)).filter(
            Comissao.profissional_id == prof.id
        ).scalar() or 0

        lucro_prof = receita_prof - comissao_total_prof
        profissionais_lucro.append({'nome': prof.user.nome, 'lucro': lucro_prof})

    top_profissionais = sorted(profissionais_lucro, key=lambda x: x['lucro'], reverse=True)[:5]

    stats = {
        'receita_hoje': receita_hoje,
        'receita_7_dias': receita_7_dias,
        'receita_15_dias': receita_15_dias,
        'receita_mes': receita_mes,
        'agendamentos_concluidos': agendamentos_concluidos,
        'agendamentos_pendentes': agendamentos_pendentes,
        'agendamentos_cancelados': agendamentos_cancelados,
        'comissoes_pendentes': comissoes_pendentes,
        'comissoes_pagas': comissoes_pagas,
        'top_profissionais': top_profissionais
    }

    return render_template('dashboard/index.html', loja=loja, stats=stats)
