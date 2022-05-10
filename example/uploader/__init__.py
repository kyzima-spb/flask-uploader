from flask import Flask
from flask_uploader import init_uploader

from . import routes
from .routes.files import mongo


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'Very secret string'
    app.config['UPLOADER_ROOT_DIR'] = '/app/upload'
    app.config['MONGO_URI'] = 'mongodb://user:demo@mongo/uploader?authSource=admin'

    mongo.init_app(app)
    init_uploader(app)

    app.register_blueprint(routes.bp)

    return app
