from __future__ import annotations
from functools import wraps
import typing as t

from flask_wtf.file import FileField
from wtforms.form import Form
from wtforms.validators import (
    DataRequired,
    StopValidation,
    ValidationError,
)
from werkzeug.datastructures import FileStorage

from .. import exceptions
from .. import validators
from ..core import Uploader


__all__ = (
    'Extension',
    'extension',
    'FileRequired',
    'file_required',
    'FileSize',
    'file_size',
    'ImageSize',
    'image_size',
    'UploadField',
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
FileRequired = file_required = DataRequired
FileSize = file_size = wrap_validator(validators.FileSize)
ImageSize = image_size = wrap_validator(validators.ImageSize)


class UploadField(FileField):  # type: ignore
    """
    A form field for uploading a file and saving it using the uploader.
    """

    def __init__(
        self,
        label: t.Optional[str] = None,
        validators: t.Optional[t.List[_WTFValidator]] = None,
        *,
        uploader: Uploader,
        overwrite: bool = False,
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
            overwrite (bool):
                Overwrite existing file. Default to ``False``.
            return_url (bool):
                After saving, return the URL of the file. Default to ``False``.
            external (bool):
                Generate absolute URL. Default to ``False``.
        """
        super().__init__(label, validators, **kwargs)
        self.data: t.Optional[t.Union[str, FileStorage]] = None
        self.uploader = uploader
        self.overwrite = overwrite
        self.return_url = return_url
        self.external = external

    def populate_obj(self, obj: t.Any, name: str) -> None:
        """
        Saves the uploaded file and populates `obj.<name>` with the search ID or URL.

        Raises:
            flask_uploader.exceptions.UploadNotAllowed:
                Any error related to the inability to save the file, but not a validation error.

        Note:
            This is a destructive operation. If `obj.<name>` already exists,
            it will be overridden. Use with caution.
        """
        self.save()
        super().populate_obj(obj, name)

    def post_validate(self, form: Form, validation_stopped: bool) -> None:
        """Runs validators from the uploader."""
        if not validation_stopped and file_is_selected(self):
            try:
                self.uploader.validate(self.data)  #type: ignore
            except exceptions.ValidationError as err:
                raise ValidationError(str(err)) from err

    def save(self) -> None:
        """Saves the uploaded file."""
        if file_is_selected(self):
            lookup = self.uploader.save(
                storage=self.data,  # type: ignore
                overwrite=self.overwrite,
                skip_validation=True,
            )

            if self.return_url:
                lookup = self.uploader.get_url(lookup, external=self.external)

            self.data = lookup
