from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from .forms import LojaForm
from .models import Loja
from . import db

loja_bp = Blueprint('loja', __name__, url_prefix='/loja')

@loja_bp.route('/criar', methods=['GET', 'POST'])
@login_required
def criar_loja():
    # Se o usuário já tem uma loja, não deveria estar aqui. Redireciona para o dashboard.
    # (Essa lógica será mais robusta depois)
    if current_user.lojas:
        return redirect(url_for('dashboard.index'))

    form = LojaForm()
    if form.validate_on_submit():
        nova_loja = Loja(
            nome=form.nome.data,
            telefone=form.telefone.data,
            dominio=form.dominio.data,
            proprietario_id=current_user.id
        )
        db.session.add(nova_loja)
        db.session.commit()
        flash('Sua loja foi criada com sucesso!', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('loja/criar_loja.html', form=form, title="Crie sua Loja")
