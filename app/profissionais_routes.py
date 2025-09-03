from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from .forms import AddProfissionalForm, EditProfissionalForm
from .models import User, Profissional
from . import db
from functools import wraps

profissionais_bp = Blueprint('profissionais', __name__, url_prefix='/profissionais')

# Decorator para verificar se o usuário é proprietário
def proprietario_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'proprietario':
            abort(403) # Proibido
        return f(*args, **kwargs)
    return decorated_function

@profissionais_bp.route('/adicionar', methods=['GET', 'POST'])
@login_required
@proprietario_required
def adicionar_profissional():
    form = AddProfissionalForm()
    if form.validate_on_submit():
        # Criar o User
        new_user = User(
            username=form.username.data,
            nome=form.nome.data,
            whatsapp=form.whatsapp.data,
            role='profissional'
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.flush()

        loja_id = current_user.owned_lojas[0].id

        novo_profissional = Profissional(
            user_id=new_user.id,
            loja_id=loja_id,
            comissao_tipo=form.comissao_tipo.data,
            comissao_valor=form.comissao_valor.data
        )
        db.session.add(novo_profissional)
        db.session.commit()

        flash('Novo profissional adicionado com sucesso!', 'success')
        return redirect(url_for('profissionais.listar_profissionais'))

    return render_template('profissionais/add_profissional.html', title='Adicionar Profissional', form=form)

@profissionais_bp.route('/')
@login_required
@proprietario_required
def listar_profissionais():
    if not current_user.owned_lojas:
        flash('Você precisa criar uma loja antes de adicionar profissionais.', 'warning')
        return redirect(url_for('loja.criar_loja'))

    loja = current_user.owned_lojas[0]
    profissionais = Profissional.query.filter_by(loja_id=loja.id).all()

    return render_template('profissionais/list_profissionais.html', title='Todos os Profissionais', profissionais=profissionais)

@profissionais_bp.route('/editar/<int:user_id>', methods=['GET', 'POST'])
@login_required
@proprietario_required
def editar_profissional(user_id):
    user = User.query.get_or_404(user_id)
    if user.profissional_profile.loja not in current_user.owned_lojas:
        abort(403)

    form = EditProfissionalForm()
    if form.validate_on_submit():
        user.nome = form.nome.data
        user.whatsapp = form.whatsapp.data
        user.profissional_profile.comissao_tipo = form.comissao_tipo.data
        user.profissional_profile.comissao_valor = form.comissao_valor.data
        db.session.commit()
        flash('Profissional atualizado com sucesso!', 'success')
        return redirect(url_for('profissionais.listar_profissionais'))

    elif request.method == 'GET':
        form.nome.data = user.nome
        form.whatsapp.data = user.whatsapp
        form.comissao_tipo.data = user.profissional_profile.comissao_tipo
        form.comissao_valor.data = user.profissional_profile.comissao_valor

    return render_template('profissionais/edit_profissional.html', title='Editar Profissional', form=form, profissional_user=user)

@profissionais_bp.route('/excluir/<int:user_id>', methods=['POST'])
@login_required
@proprietario_required
def excluir_profissional(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'profissional' or user.profissional_profile.loja not in current_user.owned_lojas:
        abort(403)

    db.session.delete(user)
    db.session.commit()
    flash('Profissional excluído com sucesso!', 'success')
    return redirect(url_for('profissionais.listar_profissionais'))

# Rota para o dashboard do profissional
@profissionais_bp.route('/dashboard')
@login_required
def dashboard_profissional():
    if current_user.role != 'profissional':
        abort(403)
    return render_template('profissionais/dashboard_profissional.html', title='Meu Dashboard')
