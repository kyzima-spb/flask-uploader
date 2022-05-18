from flask import Flask
from flask_uploader import init_uploader

from . import routes
from .routes.books import mongo
from .routes.files import aws


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('instance/config.py')

    mongo.init_app(app)
    aws.init_app(app)
    init_uploader(app)

    app.register_blueprint(routes.bp)

    return app
