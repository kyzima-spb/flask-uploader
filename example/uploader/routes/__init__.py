from flask import Blueprint

from . import books
from . import photos


bp = Blueprint('site', __name__)
bp.register_blueprint(books.bp)
bp.register_blueprint(photos.bp)
