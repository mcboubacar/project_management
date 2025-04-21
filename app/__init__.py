# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager
# from flask_migrate import Migrate
# from flask_wtf.csrf import CSRFProtect
# from config import Config

# db = SQLAlchemy()
# migrate = Migrate()
# login_manager = LoginManager()
# csrf = CSRFProtect()

# def create_app(config_class=Config):
#     app = Flask(__name__)
#     app.config.from_object(config_class)

#     init_extensions(app)

#     db.init_app(app)
#     migrate.init_app(app, db)
#     login_manager.init_app(app)
#     csrf.init_app(app)

#     login_manager.login_view = 'auth.login'
#     login_manager.login_message_category = 'info'

#     from app.blueprints.auth import auth_bp
#     from app.blueprints.admin import admin_bp
#     from app.blueprints.project import project_bp
#     from app.blueprints.monitor import monitor_bp
#     from app.blueprints.reports import reports_bp

#     app.register_blueprint(auth_bp)
#     app.register_blueprint(admin_bp, url_prefix='/admin')
#     app.register_blueprint(project_bp, url_prefix='/project')
#     app.register_blueprint(monitor_bp, url_prefix='/monitor')
#     app.register_blueprint(reports_bp, url_prefix='/reports')

#     @app.context_processor
#     def inject_globals():
#         from flask import session
#         return dict(current_role=session.get('role', None))

#     return app

# from app import models

from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate, csrf  # Import direct des extensions

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialisation des extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Configuration de Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    # Enregistrement des blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.project import project_bp
    from app.blueprints.monitor import monitor_bp
    from app.blueprints.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(project_bp, url_prefix='/project')
    app.register_blueprint(monitor_bp, url_prefix='/monitor')
    app.register_blueprint(reports_bp, url_prefix='/reports')

    @app.context_processor
    def inject_globals():
        from flask import session
        return dict(current_role=session.get('role', None))

    return app

    # from app import models