from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from .forms import AddAgendamentoForm
from .models import Loja, Agendamento, Servico, Profissional
from . import db
from functools import wraps
from datetime import timedelta

agendamentos_bp = Blueprint('agendamentos', __name__, url_prefix='/agendamentos')

# Decorator para verificar se o usuário é proprietário
def proprietario_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'proprietario':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Listar todos os agendamentos
@agendamentos_bp.route('/')
@login_required
@proprietario_required
def listar_agendamentos():
    loja = current_user.owned_lojas[0]
    agendamentos = Agendamento.query.filter_by(loja_id=loja.id).order_by(Agendamento.data_hora_inicio.desc()).all()
    return render_template('agendamentos/list_agendamentos.html', title='Gerenciar Agendamentos', agendamentos=agendamentos)

@agendamentos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@proprietario_required
def adicionar_agendamento():
    loja = current_user.owned_lojas[0]
    form = AddAgendamentoForm()
    # Define as query factories para os campos de seleção
    form.servico.query_factory = lambda: Servico.query.filter_by(loja_id=loja.id).all()
    form.profissional.query_factory = lambda: Profissional.query.filter_by(loja_id=loja.id).all()

    if form.validate_on_submit():
        servico = form.servico.data
        inicio = form.data_hora.data
        fim = inicio + timedelta(minutes=servico.duracao)

        novo_agendamento = Agendamento(
            cliente_nome=form.cliente_nome.data,
            cliente_contato=form.cliente_contato.data,
            data_hora_inicio=inicio,
            data_hora_fim=fim,
            loja_id=loja.id,
            servico_id=servico.id,
            profissional_id=form.profissional.data.id
        )
        db.session.add(novo_agendamento)
        db.session.commit()
        flash('Agendamento criado com sucesso!', 'success')
        return redirect(url_for('agendamentos.listar_agendamentos'))

    return render_template('agendamentos/add_agendamento.html', title='Novo Agendamento', form=form)

@agendamentos_bp.route('/editar/<int:agendamento_id>', methods=['GET', 'POST'])
@login_required
@proprietario_required
def editar_agendamento(agendamento_id):
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    if agendamento.loja not in current_user.owned_lojas:
        abort(403)

    form = AddAgendamentoForm() # Reutilizando o formulário de adição
    loja = current_user.owned_lojas[0]
    form.servico.query_factory = lambda: Servico.query.filter_by(loja_id=loja.id).all()
    form.profissional.query_factory = lambda: Profissional.query.filter_by(loja_id=loja.id).all()

    if form.validate_on_submit():
        servico = form.servico.data
        inicio = form.data_hora.data
        fim = inicio + timedelta(minutes=servico.duracao)

        agendamento.cliente_nome = form.cliente_nome.data
        agendamento.cliente_contato = form.cliente_contato.data
        agendamento.data_hora_inicio = inicio
        agendamento.data_hora_fim = fim
        agendamento.servico_id = servico.id
        agendamento.profissional_id = form.profissional.data.id
        # O status pode ser editado aqui também, se adicionado ao form
        db.session.commit()
        flash('Agendamento atualizado com sucesso!', 'success')
        return redirect(url_for('agendamentos.listar_agendamentos'))

    elif request.method == 'GET':
        form.cliente_nome.data = agendamento.cliente_nome
        form.cliente_contato.data = agendamento.cliente_contato
        form.data_hora.data = agendamento.data_hora_inicio
        form.servico.data = agendamento.servico
        form.profissional.data = agendamento.profissional

    return render_template('agendamentos/edit_agendamento.html', title='Editar Agendamento', form=form)

@agendamentos_bp.route('/cancelar/<int:agendamento_id>', methods=['POST'])
@login_required
@proprietario_required
def cancelar_agendamento(agendamento_id):
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    if agendamento.loja not in current_user.owned_lojas:
        abort(403)

    agendamento.status = 'cancelado'
    db.session.commit()
    flash('Agendamento cancelado com sucesso.', 'info')
    return redirect(url_for('agendamentos.listar_agendamentos'))

@agendamentos_bp.route('/concluir/<int:agendamento_id>', methods=['POST'])
@login_required
@proprietario_required
def concluir_agendamento(agendamento_id):
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    if agendamento.loja not in current_user.owned_lojas:
        abort(403)

    agendamento.status = 'concluido'
    db.session.commit()
    flash('Agendamento marcado como concluído!', 'success')
    return redirect(url_for('agendamentos.listar_agendamentos'))
