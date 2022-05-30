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

from ..forms import BookForm
from ..models import Book, Manager


bp = Blueprint('books', __name__, url_prefix='/books')
book_manager = Manager[Book](Book, 'books')


@bp.route('/', methods=['GET', 'POST'])
def index():
    form = BookForm()

    if form.validate_on_submit():
        try:
            book = Book()
            form.populate_obj(book)
            book_manager.save(book)
            flash(f'Book saved successfully.')
            return redirect(request.url)
        except UploadNotAllowed as err:
            form.file.errors.append(str(err))

    return render_template('books.html', form=form, books=book_manager.find())


@bp.route('/edit/<ObjectId:id>', methods=['GET', 'POST'])
def edit(id):
    book = book_manager.get(id)

    if book is None:
        abort(404)

    form = BookForm(obj=book)

    if form.validate_on_submit():
        try:
            form.populate_obj(book)
            book_manager.save(book)
            flash(f'Book saved successfully.')
            return redirect(request.url)
        except UploadNotAllowed as err:
            form.file.errors.append(str(err))

    return render_template('books.html', form=form)


@bp.route('/remove/<ObjectId:id>', methods=['POST'])
def remove(id):
    book = book_manager.get(id)

    if book is not None:
        books_uploader = Uploader.get_instance('books')
        books_uploader.remove(book.file)
        book_manager.delete(book)

    return redirect(url_for('.index'))
