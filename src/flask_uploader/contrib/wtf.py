from __future__ import annotations
from functools import wraps
import typing as t

from flask_wtf.file import FileField
from wtforms.form import Form
from wtforms.validators import StopValidation, ValidationError
from werkzeug.datastructures import FileStorage

from .. import exceptions
from .. import validators
from ..core import Uploader


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
_WTFValidator = t.Callable[[Form, FileField], None]


def file_is_selected(field: FileField) -> bool:
    """Returns true if the user has uploaded a file, false otherwise."""
    return bool(isinstance(field.data, FileStorage) and field.data)


def wrap_validator(cls: _F) -> _F:
    """Converts the Flask-Uploader validator to a WTForms validator."""

    @wraps(cls)
    def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Any:
        validator = cls(*args, **kwargs)

        def _validate(form: Form, field: FileField) -> None:
            if file_is_selected(field):
                try:
                    validator(field.data)
                except exceptions.ValidationError as err:
                    raise StopValidation(str(err)) from err

        return _validate

    return t.cast(_F, wrapper)


Extension = extension = wrap_validator(validators.Extension)
FileSize = file_size = wrap_validator(validators.FileSize)
ImageSize = image_size = wrap_validator(validators.ImageSize)
MimeType = mime_type = wrap_validator(validators.MimeType)


class UploaderField(FileField):  # type: ignore
    """
    A form field for uploading a file and saving it using the uploader.
    """

    def __init__(
        self,
        label: t.Optional[str] = None,
        validators: t.Optional[t.List[_WTFValidator]] = None,
        *,
        uploader: Uploader,
        return_url: bool = False,
        external: bool = False,
        **kwargs: t.Any,
    ) -> None:
        """
        Construct a new file field.

        Arguments:
            label (str):
                The label of the field.
            validators (list):
                A sequence of validators to call when `validate` is called.
            uploader (Uploader):
                File uploader instance.
            return_url (bool):
                After saving, return the URL of the file.
            external (bool):
                Generate absolute URL. Default to ``False``.
        """
        super().__init__(label, validators, **kwargs)
        self.uploader = uploader
        self.return_url = return_url
        self.external = external

    def post_validate(self, form: Form, validation_stopped: bool) -> None:
        if not validation_stopped and file_is_selected(self):
            try:
                self.uploader.validate(self.data)
            except exceptions.ValidationError as err:
                raise ValidationError(str(err)) from err

    def save(self, overwrite: bool = False) -> str:
        """
        Saves the uploaded file.

        Arguments:
            overwrite (bool):
                Overwrite existing file. Default to ``False``.
        """
        if not file_is_selected(self):
            return ''

        lookup = self.uploader.save(
            storage=self.data,
            overwrite=overwrite,
            skip_validation=True,
        )

        if self.return_url:
            lookup = self.uploader.get_url(lookup, external=self.external)

        return lookup
