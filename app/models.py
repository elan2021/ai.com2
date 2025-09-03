from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Proprietario(UserMixin, db.Model):
    """Model para os proprietários das lojas."""
    __tablename__ = 'proprietarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    whatsapp = db.Column(db.String(20), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

    lojas = db.relationship('Loja', backref='proprietario', lazy=True)

    def set_password(self, password):
        """Cria um hash para a senha."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha corresponde ao hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Proprietario {self.username}>'

class Loja(db.Model):
    """Model para as lojas."""
    __tablename__ = 'lojas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    dominio = db.Column(db.String(100), unique=True, nullable=False)
    proprietario_id = db.Column(db.Integer, db.ForeignKey('proprietarios.id'), nullable=False)

    def __repr__(self):
        return f'<Loja {self.nome}>'
