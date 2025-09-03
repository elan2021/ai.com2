from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/home')
def index():
    return "<h1>Página Principal (Placeholder)</h1>"
