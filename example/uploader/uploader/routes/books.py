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
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from flask_pymongo import PyMongo
from flask_uploader import Uploader
from flask_uploader.contrib.pymongo import GridFSStorage, Lookup, iter_files
from flask_uploader.exceptions import UploaderException, UploadNotAllowed
from flask_uploader.validators import MimeType
from wtforms import fields
from wtforms import validators


mongo = PyMongo()

bp = Blueprint('books', __name__, url_prefix='/books')

books_uploader = Uploader(
    'books',
    GridFSStorage(mongo, 'books'),
    validators=[
        MimeType(MimeType.BOOKS),
    ]
)


class BookForm(FlaskForm):
    title = fields.StringField(validators=[
        validators.InputRequired(),
        validators.Length(min=4, max=255),
    ])
    file = FileField(
        validators=[
            FileRequired(),
        ]
    )


@bp.route('/', methods=['GET', 'POST'])
def index():
    form = BookForm()

    if form.validate_on_submit():
        try:
            lookup: Lookup = books_uploader.save(form.file.data, overwrite=True)
            mongo.db.books.insert_one({
                'title': form.title.data,
                'file': lookup.oid,
            })
            flash(f'File saved successfully - {lookup}.')
            return redirect(request.url)
        except UploadNotAllowed as err:
            form.file.errors.append(str(err))
        except UploaderException as err:
            abort(500, str(err))

    return render_template(
        'books.html',
        form=form,
        uploader=books_uploader,
        files=iter_files(books_uploader.storage)
    )


@bp.route('/remove/<path:lookup>', methods=['POST'])
def remove(lookup):
    books_uploader.remove(lookup)
    return redirect(url_for('.index'))
