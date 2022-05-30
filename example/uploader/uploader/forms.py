from flask_uploader import Uploader
from flask_uploader.contrib.pymongo import GridFSStorage
from flask_uploader.contrib.wtf import (
    Extension,
    FileSize,
    MimeType,
    UploaderField,
)
from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField,
    PasswordField,
)
from flask_wtf.file import FileField
from wtforms.validators import (
    DataRequired,
    Length,
)
from werkzeug.datastructures import FileStorage

from .models import mongo


class MongoFileField(FileField):
    def populate_obj(self, obj, name):
        if isinstance(self.data, FileStorage):
            setattr(obj, name, {
                'contentType': self.data.mimetype,
                'content': self.data.stream.read(),
            })


class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired(), Length(min=1)])
    password = PasswordField(validators=[DataRequired(), Length(min=1)])


class BookForm(FlaskForm):
    title = StringField(validators=[
        DataRequired(),
        Length(min=4, max=255),
    ])
    cover = MongoFileField(validators=[
        DataRequired(),
        Extension(Extension.IMAGES),
        FileSize('1m'),
    ])
    file = UploaderField(
        uploader=Uploader('books', GridFSStorage(mongo, 'books')),
        validators=[
            DataRequired(),
            MimeType(MimeType.BOOKS),
        ],
    )
