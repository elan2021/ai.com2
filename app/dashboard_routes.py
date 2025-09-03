from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    # Por enquanto, apenas renderiza a página de boas-vindas.
    # A lógica para selecionar a loja pode ser adicionada aqui depois.
    loja = current_user.lojas[0] if current_user.lojas else None
    if not loja:
        # Isso não deveria acontecer se o fluxo de login estiver correto, mas é uma segurança
        return redirect(url_for('loja.criar_loja'))

    return render_template('dashboard/index.html', loja=loja)
