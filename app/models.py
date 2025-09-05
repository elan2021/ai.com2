import secrets
from . import db
from flask_login import UserMixin
from sqlalchemy import Time
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    """Modelo de usuário genérico para Proprietários e Profissionais."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    whatsapp = db.Column(db.String(20), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    role = db.Column(db.String(20), nullable=False, default='profissional') # 'proprietario' ou 'profissional'

    # Relacionamento para quando o usuário é um proprietário
    owned_lojas = db.relationship('Loja', foreign_keys='Loja.owner_id', backref='owner', lazy=True)

    # Relacionamento para quando o usuário é um profissional
    profissional_profile = db.relationship('Profissional', backref='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

class Loja(db.Model):
    """Model para as lojas."""
    __tablename__ = 'lojas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    dominio = db.Column(db.String(100), unique=True, nullable=False)
    api_key = db.Column(db.String(32), unique=True, nullable=False, default=lambda: secrets.token_hex(16))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    profissionais = db.relationship('Profissional', backref='loja', lazy=True, cascade="all, delete-orphan")
    servicos = db.relationship('Servico', backref='loja', lazy=True, cascade="all, delete-orphan")
    agendamentos = db.relationship('Agendamento', backref='loja', lazy=True, cascade="all, delete-orphan")
    clientes = db.relationship('Cliente', backref='loja', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Loja {self.nome}>'

# Tabela de associação para a relação muitos-para-muitos
profissional_servico_association = db.Table('profissional_servico',
    db.Column('profissional_id', db.Integer, db.ForeignKey('profissionais.id'), primary_key=True),
    db.Column('servico_id', db.Integer, db.ForeignKey('servicos.id'), primary_key=True)
)

class Profissional(db.Model):
    """Model para o perfil do profissional, com detalhes de comissão."""
    __tablename__ = 'profissionais'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    loja_id = db.Column(db.Integer, db.ForeignKey('lojas.id'), nullable=False)

    comissao_tipo = db.Column(db.String(20), nullable=False, default='porcentagem') # 'porcentagem' ou 'fixo'
    comissao_valor = db.Column(db.Float, nullable=False, default=0.0)

    servicos = db.relationship('Servico', secondary=profissional_servico_association,
                               back_populates='profissionais', lazy='dynamic')
    agendamentos = db.relationship('Agendamento', backref='profissional', lazy=True)
    horarios = db.relationship('HorarioTrabalho', backref='profissional', lazy=True, cascade="all, delete-orphan")
    comissoes = db.relationship('Comissao', backref='profissional', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Profissional Profile for User {self.user_id}>'

class Servico(db.Model):
    """Model para os serviços oferecidos pela loja."""
    __tablename__ = 'servicos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    duracao = db.Column(db.Integer, nullable=False) # Duração em minutos
    preco = db.Column(db.Float, nullable=False)
    loja_id = db.Column(db.Integer, db.ForeignKey('lojas.id'), nullable=False)

    profissionais = db.relationship('Profissional', secondary=profissional_servico_association,
                                    back_populates='servicos', lazy='dynamic')
    agendamentos = db.relationship('Agendamento', backref='servico', lazy=True)

    def __repr__(self):
        return f'<Servico {self.nome}>'

class Agendamento(db.Model):
    """Model para os agendamentos."""
    __tablename__ = 'agendamentos'

    id = db.Column(db.Integer, primary_key=True)
    data_hora_inicio = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_hora_fim = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='agendado') # agendado, concluido, cancelado

    loja_id = db.Column(db.Integer, db.ForeignKey('lojas.id'), nullable=False)
    profissional_id = db.Column(db.Integer, db.ForeignKey('profissionais.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)

    comissao = db.relationship('Comissao', backref='agendamento', uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Agendamento {self.id} em {self.data_hora_inicio}>'

class HorarioTrabalho(db.Model):
    """Model para os horários de trabalho de um profissional."""
    __tablename__ = 'horarios_trabalho'

    id = db.Column(db.Integer, primary_key=True)
    # 0: Segunda, 1: Terça, ..., 6: Domingo
    dia_da_semana = db.Column(db.Integer, nullable=False)
    horario_inicio = db.Column(Time, nullable=True)
    horario_fim = db.Column(Time, nullable=True)
    almoco_inicio = db.Column(Time, nullable=True)
    almoco_fim = db.Column(Time, nullable=True)
    pausa_entre_atendimentos = db.Column(db.Integer, nullable=True) # em minutos
    e_folga = db.Column(db.Boolean, nullable=False, default=True)
    profissional_id = db.Column(db.Integer, db.ForeignKey('profissionais.id'), nullable=False)

    def __repr__(self):
        return f'<Horario para Profissional {self.profissional_id} no dia {self.dia_da_semana}>'

class Comissao(db.Model):
    """Model para as comissões a serem pagas aos profissionais."""
    __tablename__ = 'comissoes'

    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pendente') # pendente, paga
    data_geracao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_pagamento = db.Column(db.DateTime, nullable=True)

    agendamento_id = db.Column(db.Integer, db.ForeignKey('agendamentos.id'), nullable=False)
    profissional_id = db.Column(db.Integer, db.ForeignKey('profissionais.id'), nullable=False)

    def __repr__(self):
        return f'<Comissao {self.id} - R${self.valor}>'

class Cliente(db.Model):
    """Model para os clientes da loja."""
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    loja_id = db.Column(db.Integer, db.ForeignKey('lojas.id'), nullable=False)

    agendamentos = db.relationship('Agendamento', backref='cliente', lazy=True)

    def __repr__(self):
        return f'<Cliente {self.nome}>'
