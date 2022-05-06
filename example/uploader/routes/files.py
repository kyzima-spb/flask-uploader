import os

from flask import Blueprint, render_template, request, redirect,url_for
from flask_uploader import Uploader
from flask_uploader.formats import guess_type
from flask_uploader.storages import FileSystemStorage
from flask_uploader import validators as v


bp = Blueprint('files', __name__, url_prefix='/files')
files_uploader = Uploader(
    'files',
    FileSystemStorage(dest='.'),
    validators=[
        # v.ExtensionValidator(v.ExtensionValidator.IMAGES)
        # v.MimeTypeValidator(v.MimeTypeValidator.WPS_OFFICE)
    ]
)
# files = FileSystemUploader('files', dest='uploads', endpoint='main.download_file')


# @bp.route('/custom/path/<path:lookup>')
# def download_file(lookup):
#     return files.get_url(lookup)


def iter_files():
    upload_dir = files_uploader.storage.get_root_dir()

    for root, dirs, files in os.walk(upload_dir):
        for f in files:
            path = os.path.abspath(os.path.join(root, f))
            lookup = os.path.relpath(path, upload_dir)
            url = files_uploader.get_url(lookup)
            yield lookup, url, guess_type(url, use_external=True)


@bp.route('/')
def list():
    files = iter_files()
    return render_template('list.html', files=files)


@bp.route('/remove/<path:lookup>', methods=['POST'])
def remove(lookup):
    files_uploader.remove(lookup)
    return redirect(url_for('.list'))


@bp.route('/', methods=['POST'])
def upload():
    files_uploader.save(request.files['file'], overwrite=True)
    return redirect(url_for('.list'))
