from flask import Blueprint, render_template
from pythoninfo import pythoninfo

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


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/info')
def info():
    return pythoninfo()
