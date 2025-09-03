import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=True)

    # Configure app
    app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-segura' # Trocar por variável de ambiente
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///saas.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .models import Proprietario

    @login_manager.user_loader
    def load_user(user_id):
        return Proprietario.query.get(int(user_id))

    with app.app_context():
        # Import parts of our application
        from .main_routes import main_bp
        from .auth_routes import auth_bp
        from .loja_routes import loja_bp
        from .dashboard_routes import dashboard_bp
        from .profile_routes import profile_bp

        # Register Blueprints
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(loja_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(profile_bp)

        # Create database tables for our models
        db.create_all()

        return app
