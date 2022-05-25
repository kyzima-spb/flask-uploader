from __future__ import annotations
from functools import wraps
import typing as t

from flask_wtf.file import FileField
from wtforms.form import Form
from wtforms.validators import StopValidation

from .. import validators
from ..exceptions import ValidationError


__all__ = (
    'Extension',
    'extension',
    'FileSize',
    'file_size',
    'ImageSize',
    'image_size',
    'MimeType',
    'mime_type',
)


_F = t.TypeVar('_F', bound=t.Callable[..., t.Any])


def wrap_validator(cls: _F) -> _F:
    @wraps(cls)
    def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Any:
        validator = cls(*args, **kwargs)

        def _validate(form: Form, field: FileField) -> None:
            try:
                validator(field.data)
            except ValidationError as err:
                raise StopValidation(str(err)) from err

        return _validate

    return t.cast(_F, wrapper)


Extension = extension = wrap_validator(validators.Extension)
FileSize = file_size = wrap_validator(validators.FileSize)
ImageSize = image_size = wrap_validator(validators.ImageSize)
MimeType = mime_type = wrap_validator(validators.MimeType)
