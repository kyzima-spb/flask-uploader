from flask import Flask
from flask_uploader import init_uploader
from flask_useful.app import (
    config_from_prefixed_env,
    config_from_secrets_env,
)

from . import routes
from .extensions import csrf, login_manager, aws
from .models import mongo


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    config_from_prefixed_env(app)
    config_from_secrets_env(app)

    csrf.init_app(app)
    login_manager.init_app(app)
    mongo.init_app(app)
    aws.init_app(app)
    init_uploader(app)

    app.register_blueprint(routes.bp)

    return app
