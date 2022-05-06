from flask import Blueprint

from . import photos


bp = Blueprint('site', __name__)
bp.register_blueprint(photos.bp)
