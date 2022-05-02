from __future__ import annotations
from abc import ABCMeta, abstractmethod
import os
import typing as t

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .utils import md5file, md5stream, split_pairs


class File:
    __slots__ = (
        'path_or_file',
        'filename',
        'mimetype',
    )

    def __init__(
        self,
        path_or_file: t.Union[os.PathLike, str, t.BinaryIO],
        filename: t.Optional[str] = None,
        mimetype: t.Optional[str] = None,
    ):
        self.path_or_file = path_or_file
        self.filename = filename
        self.mimetype = mimetype

    @property
    def stream(self) -> t.BinaryIO:
        if isinstance(self.path_or_file, (str, os.PathLike)):
            return open(self.path_or_file, 'rb')
        return self.path_or_file

    @property
    def hash(self):
        return md5stream(self.stream)


class AbstractStorage(metaclass=ABCMeta):
    def get_url(self) -> t.Optional[str]:
        return None

    @abstractmethod
    def load(self, lookup: str) -> File:
        """Reads and returns a ``File`` object for an identifier."""

    @abstractmethod
    def save(self, storage: FileStorage) -> str:
        """Saves the uploaded file and returns an identifier for searching."""
