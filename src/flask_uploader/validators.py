from __future__ import annotations
import re
import typing as t

from PIL import Image, UnidentifiedImageError
from werkzeug.datastructures import FileStorage

from . import formats
from .exceptions import ValidationError
from .utils import get_extension


__all__ = (
    'Extension',
    'FileRequired',
    'FileSize',
    'ImageSize',
    'MimeType',
    'TValidator',
)

TValidator = t.Callable[[FileStorage], None]


class Extension:
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


class FileRequired:
    """
    The validator checks that the file has been selected and submitted.
    """

    def __call__(self, storage: FileStorage) -> None:
        if not storage.filename:
            raise ValidationError(f'The file "{storage.name}" is required.')


class FileSize:
    """
    The validator checks that the file size is not larger than the given.
    """

    _units = ('b', 'k', 'm', 'g', 't', 'p')

    def __init__(self, max_size: t.Union[float, str]) -> None:
        """
        Arguments:
            max_size (float|str):
                The maximum file size.
                Can be an integer number of bytes, or a string with a size suffix:
                b, k, m, g, t, p.
                For example: 512m or 512Mb
        """
        if isinstance(max_size, str):
            max_size = self.to_bytes(max_size)
        self.max_size = max_size

    def __call__(self, storage: FileStorage) -> None:
        storage.stream.seek(0, 2)
        size = storage.stream.tell()
        storage.stream.seek(0)

        if size > self.max_size:
            raise ValidationError(
                f'The size of the uploaded file cannot be more than {self.to_human()}.'
            )

    def to_bytes(self, max_size: str) -> float:
        """Returns the maximum file size in bytes from a human readable string."""
        match = re.search(r'^(\d+(?:\.\d+)?)([kmgtp])b?$', max_size, re.I)

        if match is None:
            raise ValueError(f'Valid value is number with unit: {self._units}')

        k = self._units.index(match.group(2).lower())
        value = float(match.group(1))

        return value * 1024.0 ** k

    def to_human(self) -> str:
        """Returns the maximum file size in human readable format."""
        for k, unit in enumerate(self._units):
            value = self.max_size / 1024 ** k
            if value < 1024:
                unit = f'{unit}b' if k > 0 else unit
                return f'{value:3.1f}{unit.title()}'
        return f'{self.max_size:3.1f}'


class ImageSize:
    def __init__(
        self,
        min_width: t.Optional[int] = None,
        min_height: t.Optional[int] = None,
        max_width: t.Optional[int] = None,
        max_height: t.Optional[int] = None,
    ) -> None:
        if min_width is not None and max_width is not None:
            if min_width > max_width:
                raise ValueError('The minimum width must be less than the maximum.')

        if min_height is not None and max_height is not None:
            if min_height > max_height:
                raise ValueError('The minimum height must be less than the maximum.')

        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height

    def __call__(self, storage: FileStorage) -> None:
        try:
            image = Image.open(storage.stream)
        except UnidentifiedImageError as err:
            raise ValidationError('Unsupported image type.') from err

        self.validate_image(image)
        storage.stream.seek(0)

    def validate_image(self, image: Image.Image) -> None:
        width, height = image.size

        if self.min_width is not None and width < self.min_width:
            raise ValidationError(
                f'The width of the image must be greater than or equal to {self.min_width}px.'
            )

        if self.max_width is not None and width > self.max_width:
            raise ValidationError(
                f'The image width must be less than or equal to {self.max_width}px.'
            )

        if self.min_height is not None and height < self.min_height:
            raise ValidationError(
                f'The height of the image must be greater than or equal to {self.min_height}px.'
            )

        if self.max_height is not None and height > self.max_height:
            raise ValidationError(
                f'The image height must be less than or equal to {self.max_height}px.'
            )


class MimeType:
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
