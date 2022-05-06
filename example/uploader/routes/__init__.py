from flask import Blueprint

from . import files


bp = Blueprint('site', __name__)
bp.register_blueprint(files.bp)
