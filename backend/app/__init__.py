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

    with app.app_context():
        db.create_all()

    return app
