from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from .models import Proprietario, Loja

class LoginForm(FlaskForm):
    """Formulário de login."""
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar', render_kw={'name': 'login-submit'})

class CadastroForm(FlaskForm):
    """Formulário de cadastro de proprietário."""
    nome = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=100)])
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais.')])
    whatsapp = StringField('WhatsApp', validators=[DataRequired(), Length(min=10, max=20)])
    submit = SubmitField('Cadastrar', render_kw={'name': 'cadastro-submit'})

    def validate_username(self, username):
        """Valida se o nome de usuário já existe."""
        user = Proprietario.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')

class LojaForm(FlaskForm):
    """Formulário para criar/editar uma loja."""
    nome = StringField('Nome da Loja', validators=[DataRequired(), Length(min=3, max=100)])
    telefone = StringField('Telefone', validators=[DataRequired(), Length(min=10, max=20)])
    dominio = StringField('Domínio (Ex: nomedaloja)', validators=[DataRequired(), Length(min=3, max=100)])
    submit = SubmitField('Salvar Loja')

    def validate_dominio(self, dominio):
        """Valida se o domínio da loja já existe."""
        loja = Loja.query.filter_by(dominio=dominio.data).first()
        if loja:
            raise ValidationError('Este domínio já está em uso. Por favor, escolha outro.')
