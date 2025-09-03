from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

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
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    profissionais = db.relationship('Profissional', backref='loja', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Loja {self.nome}>'

class Profissional(db.Model):
    """Model para o perfil do profissional, com detalhes de comissão."""
    __tablename__ = 'profissionais'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    loja_id = db.Column(db.Integer, db.ForeignKey('lojas.id'), nullable=False)

    comissao_tipo = db.Column(db.String(20), nullable=False, default='porcentagem') # 'porcentagem' ou 'fixo'
    comissao_valor = db.Column(db.Float, nullable=False, default=0.0)

    def __repr__(self):
        return f'<Profissional Profile for User {self.user_id}>'
