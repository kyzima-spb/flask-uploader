from flask import Flask
from flask_uploader import init_uploader

from . import routes
from .extensions import csrf, login_manager, aws
from .models import mongo


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    csrf.init_app(app)
    login_manager.init_app(app)
    mongo.init_app(app)
    aws.init_app(app)
    init_uploader(app)

    app.register_blueprint(routes.bp)

    return app
