from __future__ import annotations

import os
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
)


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
    # They are generally safe to accept,
    # as without an existing RCE vulnerability,
    # they cannot be compiled, assembled, linked, or executed.
    SOURCE = frozenset(f.extension for f in formats.SOURCE)

    # Shared libraries and executable file formats
    EXECUTABLES = frozenset(f.extension for f in formats.EXECUTABLES)

    def __init__(
        self,
        extensions: t.Union[t.Set[str], frozenset[str]],
        message: t.Optional[str] = None,
    ) -> None:
        """
        Arguments:
            extensions (set|frozenset):
                Allowed file extensions.
            message (str):
                Error message to raise in case of a validation error.
        """
        self.extensions = extensions
        self.message = message

    def __call__(self, storage: FileStorage) -> None:
        if storage.filename is None:
            ext = ''
        else:
            ext = get_extension(storage.filename)

        if not ext:
            message = self.message or 'The file has no extension.'
            raise ValidationError(message)

        ext = ext.lower().lstrip('.')

        if ext not in self.extensions:
            message = self.message or 'This file type is not allowed to be uploaded.'
            raise ValidationError(message)


class FileRequired:
    """
    The validator checks that the file has been selected and submitted.
    """

    def __init__(self, message: t.Optional[str] = None) -> None:
        """
        Arguments:
            message (str):
                Error message to raise in case of a validation error.
        """
        if not message:
            message = 'The file "%(filename)s" is required.'
        self.message = message

    def __call__(self, storage: FileStorage) -> None:
        if not storage:
            raise ValidationError(self.message % {'filename': storage.name})


class FileSize:
    """
    The validator checks that the file size is not larger than the given.
    """

    _units = ('b', 'k', 'm', 'g', 't', 'p')

    def __init__(
        self,
        max_size: t.Union[float, str],
        min_size: t.Union[float, str] = 0,
        message: t.Optional[str] = None,
    ) -> None:
        """
        Arguments:
            max_size (float|str):
                The maximum file size.
                Can be an integer number of bytes,
                or a string with a size suffix:
                b, k, m, g, t, p.
                For example: 512m or 512Mb
            min_size (float|str):
                The minimum file size.
                Can be an integer number of bytes,
                or a string with a size suffix:
                b, k, m, g, t, p.
                For example: 512m or 512Mb
            message (str):
                Error message to raise in case of a validation error.
        """
        if isinstance(min_size, str):
            min_size = self.to_bytes(min_size)

        if isinstance(max_size, str):
            max_size = self.to_bytes(max_size)

        if min_size > max_size:
            raise ValueError(
                'The minimum size must be less than the maximum size.'
            )

        if not message:
            message = (
                'The size of the uploaded file '
                'must be between %(min_size)s and %(max_size)s.'
            )

        self.min_size = min_size
        self.max_size = max_size
        self.message = message

    def __call__(self, storage: FileStorage) -> None:
        storage.stream.seek(0, os.SEEK_END)
        size = storage.stream.tell()
        storage.stream.seek(0)

        if not(self.min_size <= size <= self.max_size):
            raise ValidationError(self.format_message(self.message))

    def format_message(self, message: str, **kwargs: t.Any) -> str:
        return message % {
            'min_size': self.to_human(self.min_size),
            'max_size': self.to_human(self.max_size),
            **kwargs,
        }

    def to_bytes(self, size: str) -> float:
        """
        Returns the maximum file size in bytes from a human readable string.
        """
        match = re.search(r'^(\d+(?:\.\d+)?)([kmgtp]?)b?$', size, re.I)

        if match is None:
            raise ValueError(f'Valid value is number with unit: {self._units}')

        value = float(match.group(1))

        if match.group(2):
            k = self._units.index(match.group(2).lower())
            return value * 1024.0 ** k

        return value

    def to_human(self, size: float) -> str:
        """Returns the file size in human readable format."""
        for k, unit in enumerate(self._units):
            value = size / 1024 ** k
            if value < 1024:
                unit = f'{unit}b' if k > 0 else unit
                return f'{value:3.1f}{unit.title()}'
        return f'{size:3.1f}'


class ImageSize:
    """
    The validator checks the image size in pixels.
    """

    EXACT_SIZE = 'Image size should be %(min_width)dx%(min_height)dpx.'
    EXACT_WIDTH = 'Image width should be equal %(min_width)dpx.'
    EXACT_HEIGHT = 'Image height should be equal %(min_height)dpx.'
    SIZE_GREATER_EQUAL = 'Image size must be greater than or equal to %(min_width)dx%(min_height)dpx.'
    SIZE_LESS_EQUAL = 'Image size must be less than or equal to %(max_width)dx%(max_height)dpx.'
    WIDTH_GREATER_EQUAL = 'Image width must be greater than or equal to %(min_width)dpx.'
    HEIGHT_GREATER_EQUAL = 'Image height must be greater than or equal to %(min_height)dpx.'
    WIDTH_LESS_EQUAL = 'Image width must be less than or equal to %(max_width)dpx.'
    HEIGHT_LESS_EQUAL = 'Image height must be less than or equal to %(max_height)dpx.'

    def __init__(
        self,
        min_width: int = -1,
        min_height: int = -1,
        max_width: int = -1,
        max_height: int = -1,
        message: t.Optional[str] = None,
    ) -> None:
        if (
            min_width < 0 and max_width < 0
            and
            min_height < 0 and max_height < 0
        ):
            raise ValueError('At least one of the size options must be given.')

        if min_width >= 0 and 0 <= max_width < min_width:
            raise ValueError(
                'The minimum width must be less than the maximum.'
            )

        if min_height >= 0 and 0 <= max_height < min_height:
            raise ValueError(
                'The minimum height must be less than the maximum.'
            )

        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height
        self.message = message

    def __call__(self, storage: FileStorage) -> None:
        try:
            image = Image.open(storage.stream)
        except UnidentifiedImageError as err:
            message = 'Unsupported image type.' if self.message is None else self.message
            raise ValidationError(self.format_message(message)) from err

        self.validate_image(image)
        storage.stream.seek(0)

    def format_message(self, message: str, **kwargs: t.Any) -> str:
        return message % {
            'min_width': self.min_width,
            'min_height': self.min_height,
            'max_width': self.max_width,
            'max_height': self.max_height,
            **kwargs,
        }

    def validate_image(self, image: Image.Image) -> None:
        width, height = image.size
        invalid = (
            self.min_width >= 0 and self.min_width > width
            or
            self.min_height >= 0 and self.min_height > height
            or
            0 <= self.max_width < width
            or
            0 <= self.max_height < height
        )

        if invalid:
            message = 'Invalid image size.' if self.message is None else self.message
            raise ValidationError(
                self.format_message(message, width=width, height=height)
            )
