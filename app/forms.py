from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField, IntegerField, SelectMultipleField, BooleanField, FormField
from wtforms.fields import DateTimeField, TimeField
from wtforms.form import Form
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError, NumberRange, Optional
from .models import User, Loja
from flask_login import current_user

class LoginForm(FlaskForm):
    """Formulário de login."""
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class CadastroForm(FlaskForm):
    """Formulário de cadastro de proprietário."""
    nome = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=100)])
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais.')])
    whatsapp = StringField('WhatsApp', validators=[DataRequired(), Length(min=10, max=20)])
    submit = SubmitField('Cadastrar')

    def validate_username(self, username):
        """Valida se o nome de usuário já existe."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')

class EditProfissionalForm(FlaskForm):
    """Formulário para editar um profissional existente."""
    nome = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=100)])
    whatsapp = StringField('WhatsApp', validators=[DataRequired(), Length(min=10, max=20)])
    comissao_tipo = SelectField('Tipo de Comissão', choices=[('porcentagem', 'Porcentagem (%)'), ('fixo', 'Valor Fixo (R$)')], validators=[DataRequired()])
    comissao_valor = FloatField('Valor da Comissão', validators=[DataRequired(), NumberRange(min=0)])
    servicos = SelectMultipleField('Serviços Realizados', coerce=int)
    submit = SubmitField('Salvar Alterações')

class ServicoForm(FlaskForm):
    """Formulário para adicionar ou editar um serviço."""
    nome = StringField('Nome do Serviço', validators=[DataRequired(), Length(max=100)])
    duracao = IntegerField('Duração (em minutos)', validators=[DataRequired(), NumberRange(min=1)])
    preco = FloatField('Preço (R$)', validators=[DataRequired(), NumberRange(min=0)])
    profissionais = SelectMultipleField('Profissionais que realizam este serviço', coerce=int)
    submit = SubmitField('Salvar Serviço')

    def __init__(self, *args, **kwargs):
        super(ServicoForm, self).__init__(*args, **kwargs)
        if 'profissionais_choices' in kwargs:
            self.profissionais.choices = kwargs['profissionais_choices']

def get_pk_from_identity(obj):
    return obj.id if obj else None

def get_profissional_label(profissional):
    return profissional.user.nome

class AddAgendamentoForm(FlaskForm):
    """Formulário para adicionar um novo agendamento."""
    cliente_nome = StringField('Nome do Cliente', validators=[DataRequired()])
    cliente_contato = StringField('Contato do Cliente (Telefone/Email)')
    data_hora = DateTimeField('Data e Hora', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])

    servico = QuerySelectField('Serviço', query_factory=None, get_label='nome', get_pk=get_pk_from_identity, allow_blank=True, blank_text='-- Selecione um Serviço --')
    profissional = QuerySelectField('Profissional', query_factory=None, get_label=get_profissional_label, get_pk=get_pk_from_identity, allow_blank=True, blank_text='-- Selecione um Profissional --')

    submit = SubmitField('Salvar Agendamento')

class HorarioDiaForm(Form):
    """Sub-formulário para os horários de um único dia."""
    horario_inicio = TimeField('Início', format='%H:%M', validators=[Optional()])
    horario_fim = TimeField('Fim', format='%H:%M', validators=[Optional()])
    almoco_inicio = TimeField('Início Almoço', format='%H:%M', validators=[Optional()])
    almoco_fim = TimeField('Fim Almoço', format='%H:%M', validators=[Optional()])
    pausa_entre_atendimentos = IntegerField('Pausa (min)', validators=[Optional(), NumberRange(min=0)])
    e_folga = BooleanField('Folga')

class GerenciarHorariosForm(FlaskForm):
    """Formulário principal para gerenciar a semana inteira."""
    dias = FieldList(FormField(HorarioDiaForm), min_entries=7, max_entries=7)
    submit = SubmitField('Salvar Horários')

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

class UpdateAccountForm(FlaskForm):
    """Formulário para atualizar dados da conta."""
    nome = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=100)])
    whatsapp = StringField('WhatsApp', validators=[DataRequired(), Length(min=10, max=20)])
    picture = FileField('Atualizar Foto de Perfil', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit_account = SubmitField('Atualizar Dados')

class ChangePasswordForm(FlaskForm):
    """Formulário para alterar a senha."""
    current_password = PasswordField('Senha Atual', validators=[DataRequired()])
    new_password = PasswordField('Nova Senha', validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField('Confirmar Nova Senha', validators=[DataRequired(), EqualTo('new_password', message='As senhas devem ser iguais.')])
    submit_password = SubmitField('Alterar Senha')

class AddProfissionalForm(FlaskForm):
    """Formulário para adicionar um novo profissional."""
    nome = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=100)])
    whatsapp = StringField('WhatsApp', validators=[DataRequired(), Length(min=10, max=20)])
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais.')])

    comissao_tipo = SelectField('Tipo de Comissão', choices=[('porcentagem', 'Porcentagem (%)'), ('fixo', 'Valor Fixo (R$)')], validators=[DataRequired()])
    comissao_valor = FloatField('Valor da Comissão', validators=[DataRequired(), NumberRange(min=0)])

    submit = SubmitField('Adicionar Profissional')

    def validate_username(self, username):
        """Valida se o nome de usuário já existe."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')
