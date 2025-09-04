from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from .forms import ServicoForm
from .models import Servico, Profissional
from . import db
from functools import wraps

servicos_bp = Blueprint('servicos', __name__, url_prefix='/servicos')

# Decorator para verificar se o usuário é proprietário
def proprietario_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'proprietario':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Listar todos os serviços
@servicos_bp.route('/')
@login_required
@proprietario_required
def listar_servicos():
    loja = current_user.owned_lojas[0]
    servicos = loja.servicos
    return render_template('servicos/list_servicos.html', title='Gerenciar Serviços', servicos=servicos)

# Adicionar novo serviço
@servicos_bp.route('/adicionar', methods=['GET', 'POST'])
@login_required
@proprietario_required
def adicionar_servico():
    loja = current_user.owned_lojas[0]
    form = ServicoForm()
    form.profissionais.choices = [(p.id, p.user.nome) for p in Profissional.query.filter_by(loja_id=loja.id).all()]

    if form.validate_on_submit():
        novo_servico = Servico(
            nome=form.nome.data,
            duracao=form.duracao.data,
            preco=form.preco.data,
            loja_id=loja.id
        )
        for profissional_id in form.profissionais.data:
            profissional = Profissional.query.get(profissional_id)
            novo_servico.profissionais.append(profissional)

        db.session.add(novo_servico)
        db.session.commit()
        flash('Serviço adicionado com sucesso!', 'success')
        return redirect(url_for('servicos.listar_servicos'))
    return render_template('servicos/add_servico.html', title='Adicionar Serviço', form=form)

# Editar serviço
@servicos_bp.route('/editar/<int:servico_id>', methods=['GET', 'POST'])
@login_required
@proprietario_required
def editar_servico(servico_id):
    servico = Servico.query.get_or_404(servico_id)
    if servico.loja not in current_user.owned_lojas:
        abort(403)

    form = ServicoForm()
    form.profissionais.choices = [(p.id, p.user.nome) for p in Profissional.query.filter_by(loja_id=servico.loja_id).all()]

    if form.validate_on_submit():
        servico.nome = form.nome.data
        servico.duracao = form.duracao.data
        servico.preco = form.preco.data

        servico.profissionais = []
        for profissional_id in form.profissionais.data:
            profissional = Profissional.query.get(profissional_id)
            servico.profissionais.append(profissional)

        db.session.commit()
        flash('Serviço atualizado com sucesso!', 'success')
        return redirect(url_for('servicos.listar_servicos'))

    elif request.method == 'GET':
        form.nome.data = servico.nome
        form.duracao.data = servico.duracao
        form.preco.data = servico.preco
        form.profissionais.data = [p.id for p in servico.profissionais]

    return render_template('servicos/edit_servico.html', title='Editar Serviço', form=form)

# Excluir serviço
@servicos_bp.route('/excluir/<int:servico_id>', methods=['POST'])
@login_required
@proprietario_required
def excluir_servico(servico_id):
    servico = Servico.query.get_or_404(servico_id)
    if servico.loja not in current_user.owned_lojas:
        abort(403)

    db.session.delete(servico)
    db.session.commit()
    flash('Serviço excluído com sucesso!', 'success')
    return redirect(url_for('servicos.listar_servicos'))
