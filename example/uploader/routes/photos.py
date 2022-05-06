import os

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_uploader import Uploader
from flask_uploader.formats import guess_type
from flask_uploader.storages import FileSystemStorage
from flask_uploader import validators as v


bp = Blueprint('photos', __name__, url_prefix='/photos')
photos_uploader = Uploader(
    'photos',
    FileSystemStorage(dest='.'),
    validators=[
        v.ExtensionValidator(
            v.ExtensionValidator.IMAGES
        )
        # v.MimeTypeValidator(v.MimeTypeValidator.WPS_OFFICE)
    ]
)
# files = FileSystemUploader('files', dest='uploads', endpoint='main.download_file')


# @bp.route('/custom/path/<path:lookup>')
# def download_file(lookup):
#     return files.get_url(lookup)


def iter_files():
    upload_dir = photos_uploader.storage.get_root_dir()

    for root, dirs, files in os.walk(upload_dir):
        for f in files:
            path = os.path.abspath(os.path.join(root, f))
            lookup = os.path.relpath(path, upload_dir)
            url = photos_uploader.get_url(lookup)
            yield lookup, url, guess_type(url, use_external=True)


@bp.route('/')
def list():
    files = iter_files()
    return render_template('list.html', files=files)


@bp.route('/remove/<path:lookup>', methods=['POST'])
def remove(lookup):
    photos_uploader.remove(lookup)
    return redirect(request.url)


@bp.route('/', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part.')
        return redirect(request.url)

    try:
        photos_uploader.save(request.files['file'], overwrite=True)
        flash('File saved successfully.')
    except v.ValidationError as err:
        flash(str(err))

    return redirect(request.url)
