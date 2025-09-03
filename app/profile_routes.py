import os
import secrets
from PIL import Image
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from .forms import UpdateAccountForm, ChangePasswordForm
from . import db

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

def save_picture(form_picture):
    """Salva a imagem de perfil, redimensiona e retorna o nome do arquivo."""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    # Criar o diretório se não existir
    output_dir = os.path.join(current_app.root_path, 'static/profile_pics')
    os.makedirs(output_dir, exist_ok=True)

    # Redimensionar imagem
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    # Remover a foto antiga se não for a default
    if current_user.image_file != 'default.jpg':
        old_picture_path = os.path.join(current_app.root_path, 'static/profile_pics', current_user.image_file)
        if os.path.exists(old_picture_path):
            os.remove(old_picture_path)

    return picture_fn

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    account_form = UpdateAccountForm()
    password_form = ChangePasswordForm()

    if 'submit_account' in request.form and account_form.validate_on_submit():
        if account_form.picture.data:
            picture_file = save_picture(account_form.picture.data)
            current_user.image_file = picture_file
        current_user.nome = account_form.nome.data
        current_user.whatsapp = account_form.whatsapp.data
        db.session.commit()
        flash('Sua conta foi atualizada!', 'success')
        return redirect(url_for('profile.edit_profile'))

    if 'submit_password' in request.form and password_form.validate_on_submit():
        if current_user.check_password(password_form.current_password.data):
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash('Sua senha foi alterada com sucesso!', 'success')
            return redirect(url_for('profile.edit_profile'))
        else:
            flash('Senha atual incorreta.', 'danger')

    elif request.method == 'GET':
        account_form.nome.data = current_user.nome
        account_form.whatsapp.data = current_user.whatsapp

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('profile/edit.html', title='Editar Perfil',
                           account_form=account_form, password_form=password_form,
                           image_file=image_file)
