from __future__ import annotations

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from flask_pymongo import PyMongo
from flask_uploader import Uploader
from flask_uploader.contrib.pymongo import GridFSStorage, Lookup
from flask_uploader.validators import (
    MimeTypeValidator,
    ValidationError,
)
from wtforms import fields
from wtforms import validators


mongo = PyMongo()

bp = Blueprint('books', __name__, url_prefix='/books')

books_uploader = Uploader(
    'books',
    GridFSStorage(mongo, 'books'),
    validators=[
        MimeTypeValidator(MimeTypeValidator.BOOKS),
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
                'file': lookup.value,
            })
            return redirect(request.url)
        except ValidationError as err:
            form.file.errors.append(str(err))

    return render_template('books.html', form=form, uploader=books_uploader)


@bp.route('/remove/<lookup>', methods=['POST'])
def remove(lookup):
    books_uploader.remove(lookup)
    return redirect(url_for('.index'))
