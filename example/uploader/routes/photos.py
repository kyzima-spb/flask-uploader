from __future__ import annotations

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_uploader import Uploader
from flask_uploader.storages import FileSystemStorage
from flask_uploader.validators import MimeTypeValidator, ValidationError


bp = Blueprint('photos', __name__, url_prefix='/photos')

photos_uploader = Uploader(
    'photos',
    FileSystemStorage(dest='photos'),
    validators=[
        MimeTypeValidator(MimeTypeValidator.IMAGES),
    ]
)


@bp.route('/')
def index():
    return render_template('list.html', uploader=photos_uploader)


@bp.route('/remove/<path:lookup>', methods=['POST'])
def remove(lookup):
    photos_uploader.remove(lookup)
    return redirect(url_for('.index'))


@bp.route('/', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part.')
        return redirect(request.url)

    try:
        photos_uploader.save(request.files['file'], overwrite=True)
        flash('File saved successfully.')
    except ValidationError as err:
        flash(str(err))

    return redirect(request.url)
