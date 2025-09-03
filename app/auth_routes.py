from flask import Blueprint, render_template, redirect, url_for, flash, request
from .forms import LoginForm, CadastroForm
from .models import User
from . import db
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    # Se o usuário já estiver logado, redireciona para o dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    login_form = LoginForm(prefix='login')
    cadastro_form = CadastroForm(prefix='cadastro')

    # Lógica de Cadastro
    if 'cadastro-submit' in request.form and cadastro_form.validate_on_submit():
        # Cria novo usuário com a role 'proprietario'
        new_user = User(
            username=cadastro_form.username.data,
            nome=cadastro_form.nome.data,
            whatsapp=cadastro_form.whatsapp.data,
            role='proprietario'
        )
        new_user.set_password(cadastro_form.password.data)
        db.session.add(new_user)
        db.session.commit()

        flash('Cadastro realizado com sucesso! Faça o login.', 'success')
        return redirect(url_for('auth.login'))

    # Lógica de Login
    if 'login-submit' in request.form and login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and user.check_password(login_form.password.data):
            login_user(user)
            # Apenas proprietários podem ter lojas e acessar o dashboard principal
            if user.role == 'proprietario':
                if not user.owned_lojas:
                    flash('Login bem-sucedido! Agora, crie sua primeira loja.', 'info')
                    return redirect(url_for('loja.criar_loja'))
                else:
                    flash('Login bem-sucedido!', 'success')
                    return redirect(url_for('dashboard.index'))
            else:
                # Futuramente, redirecionar para o dashboard do profissional
                flash('Login de profissional bem-sucedido!', 'success')
                return redirect(url_for('main.index')) # Placeholder
        else:
            flash('Usuário ou senha inválidos.', 'danger')

    return render_template('auth.html', login_form=login_form, cadastro_form=cadastro_form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('auth.login'))
