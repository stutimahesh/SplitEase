from flask import Flask
from flask_cors import CORS

from .config import Config
from .extensions import db, jwt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    from . import models  # noqa: F401  (ensures models are registered before create_all)
    from .auth import auth_bp
    from .groups import groups_bp
    from .expenses import expenses_bp
    from .balances import balances_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(groups_bp, url_prefix="/api/groups")
    app.register_blueprint(expenses_bp, url_prefix="/api")
    app.register_blueprint(balances_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()

    return app
