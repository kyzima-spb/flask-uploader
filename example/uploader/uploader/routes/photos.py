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
from flask_uploader.exceptions import UploadNotAllowed
from flask_uploader.storages import FileSystemStorage, iter_files
from flask_uploader.validators import (
    Extension,
    ImageSize,
    FileRequired,
    FileSize,
)


bp = Blueprint('photos', __name__, url_prefix='/photos')

photos_storage = FileSystemStorage(dest='photos')
photos_uploader = Uploader(
    'photos',
    photos_storage,
    validators=[
        FileRequired(),
        FileSize('10Mb'),
        Extension(Extension.IMAGES),
        ImageSize(max_width=1920, max_height=1080),
    ]
)


@bp.route('/')
def index():
    return render_template('photos.html', files=iter_files(photos_storage))


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
        lookup = photos_uploader.save(request.files['file'], overwrite=True)
        # lookup = photos_uploader.save(request.files['file'])
        flash(f'Photo saved successfully - {lookup}.')
    except UploadNotAllowed as err:
        flash(str(err))

    return redirect(request.url)
