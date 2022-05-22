from flask import Blueprint

from . import auth
from . import books
from . import files
from . import invoices
from . import photos


bp = Blueprint('site', __name__)
bp.register_blueprint(auth.bp)
bp.register_blueprint(books.bp)
bp.register_blueprint(files.bp)
bp.register_blueprint(invoices.bp)
bp.register_blueprint(photos.bp)
