from flask import Flask
from flask_uploader import init_uploader

from . import routes


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'Very secret string'
    app.config['UPLOADER_ROOT_DIR'] = '/app/upload'
    # app.config['MONGO_URI'] = 'mongodb://user:demo@mongo/uploader?authSource=admin'
    # app.config['MONGODB_HOST'] = 'mongodb://user:demo@mongo/auth?authSource=admin'

    init_uploader(app)
    app.register_blueprint(routes.bp)
    # mongo.init_app(app)

    return app
