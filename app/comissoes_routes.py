from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from .models import Comissao, Loja
from . import db
from functools import wraps
from datetime import datetime

comissoes_bp = Blueprint('comissoes', __name__, url_prefix='/comissoes')

# Decorator para verificar se o usuário é proprietário
def proprietario_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'proprietario':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Listar todas as comissões

@comissoes_bp.route('/')
@login_required
@proprietario_required
def listar_comissoes():
    loja = current_user.owned_lojas[0]
    # Encontra todos os profissionais da loja
    profissionais_da_loja = [p.id for p in loja.profissionais]
    # Filtra as comissões por esses profissionais
    comissoes = Comissao.query.filter(Comissao.profissional_id.in_(profissionais_da_loja)).order_by(Comissao.data_geracao.desc()).all()

    return render_template('comissoes/list_comissoes.html', title='Gerenciar Comissões', comissoes=comissoes)

@comissoes_bp.route('/pagar/<int:comissao_id>', methods=['POST'])
@login_required
@proprietario_required
def pagar_comissao(comissao_id):
    comissao = Comissao.query.get_or_404(comissao_id)
    # Verifica se a comissão pertence a um profissional da loja do proprietário
    if comissao.profissional.loja not in current_user.owned_lojas:
        abort(403)

    comissao.status = 'paga'
    comissao.data_pagamento = datetime.utcnow()
    db.session.commit()
    flash(f'Comissão de R$ {comissao.valor} para {comissao.profissional.user.nome} marcada como paga.', 'success')
    return redirect(url_for('comissoes.listar_comissoes'))
