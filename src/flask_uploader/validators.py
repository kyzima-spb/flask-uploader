from __future__ import annotations
import typing as t

from PIL import Image
from werkzeug.datastructures import FileStorage

from . import formats
from .exceptions import ValidationError
from .utils import get_extension


__all__ = (
    'ExtensionValidator',
    'ImageSizeValidator',
    'MimeTypeValidator',
    'TValidator',
)

TValidator = t.Callable[[FileStorage], None]


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

    def __init__(
        self,
        extensions: t.Union[set[str], frozenset[str]]
    ) -> None:
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

    def __init__(
        self,
        mime_types: t.Union[set[str], frozenset[str]]
    ) -> None:
        self.mime_types = mime_types

    def __call__(self, storage: FileStorage) -> None:
        if storage.mimetype is None:
            raise ValidationError('There is no HTTP Content-Type header.')

        if storage.mimetype not in self.mime_types:
            raise ValidationError('This file type is not allowed to be uploaded.')


class ImageSizeValidator:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def __call__(self, storage: FileStorage) -> None:
        image = Image.open(storage.stream)
        width, height = image.size
        storage.stream.seek(0)

        if self.width < width or self.height < height:
            raise ValidationError(
                'The image size is larger than %dx%d.' % (
                    self.width, self.height
                )
            )


# def required_filename(storage: FileStorage) -> None:
#     if not storage.filename:
#         raise ValidationError('Filename is required.')
