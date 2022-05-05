from __future__ import annotations
import typing as t

from werkzeug.datastructures import FileStorage

from . import formats
from .utils import get_extension


__all__ = (
    'ExtensionValidator',
    'TValidator',
    'ValidationError',
)


class TValidator(t.Protocol):
    def __call__(self, storage: FileStorage) -> None:
        ...


class ValidationError(Exception):
    pass


UploadNotAllowed = ValidationError


class ExtensionValidator:
    """
    The validator checks the file extension.

    This is a weak type of validation.
    """

    # This just contains plain text files
    TEXT = frozenset((
        formats.TXT.extension,
    ))

    # This contains various office document formats
    MS_OFFICE = frozenset(f.extension for f in formats.MS_OFFICE)
    OPEN_OFFICE = frozenset(f.extension for f in formats.OPEN_OFFICE)
    WPS_OFFICE = frozenset(f.extension for f in formats.WPS_OFFICE)
    OFFICE = MS_OFFICE | OPEN_OFFICE | WPS_OFFICE | {
        f.extension for f in formats.OTHER_OFFICE
    }

    # This contains electronic book formats
    EDOCUMENTS = frozenset(f.extension for f in formats.EDOCUMENTS)
    EBOOKS = frozenset(f.extension for f in formats.EBOOKS)
    BOOKS = EDOCUMENTS | EBOOKS

    # This contains basic image types that are viewable from most browsers
    IMAGES = frozenset(f.extension for f in formats.IMAGES)

    # This contains audio file types
    AUDIO = frozenset(f.extension for f in formats.AUDIO)

    # This is for structured data files
    DATA = frozenset(f.extension for f in formats.DATA)

    # This contains various types of scripts
    SCRIPTS = frozenset(f.extension for f in formats.SCRIPTS)

    # This contains archive and compression formats
    ARCHIVES = frozenset(f.extension for f in formats.ARCHIVES)

    # This contains non executable source files
    # those which need to be compiled or assembled to binaries to be used.
    # They are generally safe to accept, as without an existing RCE vulnerability,
    # they cannot be compiled, assembled, linked, or executed.
    SOURCE = frozenset(f.extension for f in formats.SOURCE)

    # Shared libraries and executable file formats
    EXECUTABLES = frozenset(f.extension for f in formats.EXECUTABLES)

    def __init__(self, extensions: t.Sequence[str]):
        self.extensions = extensions

    def __call__(self, storage: FileStorage) -> None:
        ext = '' if storage.filename is None else get_extension(storage.filename)

        if not ext:
            raise ValidationError('The file has no extension.')

        ext = ext.lower().lstrip('.')

        if ext not in self.extensions:
            raise ValidationError('This file type is not allowed to be uploaded.')


class MimeTypeValidator:
    """
    The validator checks the media type passed in the Content-Type HTTP header.

    This is a weak type of validation.
    """

    # This just contains plain text files
    TEXT = frozenset((
        formats.TXT.mimetype,
    ))

    # This contains various office document formats
    MS_OFFICE = frozenset(f.mimetype for f in formats.MS_OFFICE)
    OPEN_OFFICE = frozenset(f.mimetype for f in formats.OPEN_OFFICE)
    WPS_OFFICE = frozenset(f.mimetype for f in formats.WPS_OFFICE)
    OFFICE = MS_OFFICE | OPEN_OFFICE | WPS_OFFICE | {
        f.mimetype for f in formats.OTHER_OFFICE
    }

    # This contains electronic book formats
    EDOCUMENTS = frozenset(f.mimetype for f in formats.EDOCUMENTS)
    EBOOKS = frozenset(f.mimetype for f in formats.EBOOKS)
    BOOKS = EDOCUMENTS | EBOOKS

    # This contains basic image types that are viewable from most browsers
    IMAGES = frozenset(f.mimetype for f in formats.IMAGES)

    # This contains audio file types
    AUDIO = frozenset(f.mimetype for f in formats.AUDIO)

    # This is for structured data files
    DATA = frozenset(f.mimetype for f in formats.DATA)

    # This contains various types of scripts
    SCRIPTS = frozenset(f.mimetype for f in formats.SCRIPTS)

    # This contains archive and compression formats
    ARCHIVES = frozenset(f.mimetype for f in formats.ARCHIVES)

    # This contains non executable source files
    # those which need to be compiled or assembled to binaries to be used.
    # They are generally safe to accept, as without an existing RCE vulnerability,
    # they cannot be compiled, assembled, linked, or executed.
    SOURCE = frozenset(f.mimetype for f in formats.SOURCE)

    # Shared libraries and executable file formats
    EXECUTABLES = frozenset(f.mimetype for f in formats.EXECUTABLES)

    def __init__(self, mime_types: t.Sequence[str]):
        self.mime_types = mime_types

    def __call__(self, storage: FileStorage) -> None:
        print(storage.mimetype)

        if storage.mimetype is None:
            raise ValidationError('There is no HTTP Content-Type header.')

        if storage.mimetype not in self.mime_types:
            raise ValidationError('This file type is not allowed to be uploaded.')