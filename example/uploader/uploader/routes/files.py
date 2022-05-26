from __future__ import annotations

from flask import (
    abort,
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_uploader import Uploader
from flask_uploader.exceptions import UploaderException, UploadNotAllowed
from flask_uploader.contrib.aws import AWS, S3Storage, iter_files

from werkzeug.utils import secure_filename

from ..extensions import aws


def original_filename(storage) -> str:
    # Non-ASCII characters will be removed
    # For filename '天安门.jpg' returns 'jpg'
    return secure_filename(storage.filename) if storage.filename else ''


bp = Blueprint('files', __name__, url_prefix='/files')

files_storage = S3Storage(
    aws.resource('s3'),
    'flask-uploader',
    filename_strategy=original_filename,
    key_prefix='original_names',
)
files_uploader = Uploader(
    'files',
    files_storage,
    validators=[]
)


@bp.route('/')
def index():
    return render_template('files.html', files=iter_files(files_storage))


@bp.route('/remove/<path:lookup>', methods=['POST'])
def remove(lookup):
    files_uploader.remove(lookup)
    return redirect(url_for('.index'))


@bp.route('/', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part.')
        return redirect(request.url)

    try:
        # lookup = files_uploader.save(request.files['file'], overwrite=True)
        lookup = files_uploader.save(request.files['file'])
        flash(f'File saved successfully - {lookup}.')
    except UploadNotAllowed as err:
        flash(str(err))

    return redirect(request.url)
