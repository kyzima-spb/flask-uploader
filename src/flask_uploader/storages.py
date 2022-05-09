from __future__ import annotations
from abc import ABCMeta, abstractmethod
from glob import iglob
import os
import typing as t

from flask import current_app
from werkzeug.datastructures import FileStorage
# from werkzeug.utils import secure_filename

from .formats import guess_type
from .utils import get_extension, increment_path, md5stream, split_pairs


__all__ = (
    'AbstractStorage',
    'File',
    'FileSystemStorage',
    'HashedFilenameStrategy',
    'TFilenameStrategy',
)

TFilenameStrategy = t.Callable[[FileStorage], str]


class HashedFilenameStrategy:
    """
    A strategy that generates a name by calculating a hash of the contents of a file
    and splitting it into the specified number of parts of the specified length.

    Solves the problem of storing many files on the hard disk
    when the number of files in one directory is limited by the OS.

    Thanks to the hash and partitioning, files are evenly stored across directories.
    """

    __slots__ = ('buffer_size', 'step', 'max_split')

    def __init__(
        self,
        buffer_size: int = 16384,
        step: int = 2,
        max_split: int = 3
    ) -> None:
        """
        Arguments:
            buffer_size (int):
                The buffer size is the number of bytes held in memory during the hash process.
                Default to 16Kb.
            step (int): cutting step. Default to ``2``.
            max_split (int): Maximum number of splits to do. Default to ``3``.
        """
        self.buffer_size = buffer_size
        self.step = step
        self.max_split = max_split

    def __call__(self, storage: FileStorage) -> str:
        hash = md5stream(t.cast(t.BinaryIO, storage.stream), self.buffer_size)
        *folder, name = split_pairs(
            hash, step=self.step, max_split=self.max_split
        )
        ext = ''

        if storage.filename is not None:
            ext = get_extension(storage.filename)

        return os.path.join(*folder, name) + ext


class File(t.NamedTuple):
    """The result of reading a file from the selected storage."""
    path_or_file: t.Union[str, t.BinaryIO]
    filename: t.Optional[str] = None
    mimetype: t.Optional[str] = None


class AbstractStorage(metaclass=ABCMeta):
    """A file storage that provides basic file operations."""

    __slots__ = ('filename_strategy',)

    def __init__(
        self,
        filename_strategy: t.Optional[TFilenameStrategy] = None
    ) -> None:
        """
        Arguments:
            filename_strategy (TFilenameStrategy):
                A callable that returns the name of the file to save.
        """
        if filename_strategy is None:
            filename_strategy = HashedFilenameStrategy()
        self.filename_strategy = filename_strategy

    def get_url(self, lookup: str) -> t.Optional[str]:
        """
        Returns the absolute URL for the file.

        Used only for external network storage, such as Amazon S3.
        If you just want to override the default URL,
        use the ``endpoint`` argument of the ``Uploader`` constructor.

        Arguments:
            lookup (str):
                The unique identifier for the file in the selected storage.
        """
        return None

    @abstractmethod
    def load(self, lookup: str) -> File:
        """Reads and returns a ``File`` object for an identifier."""

    @abstractmethod
    def remove(self, lookup: str) -> None:
        """Deletes a file from storage by unique identifier."""

    @abstractmethod
    def save(self, storage: FileStorage, overwrite: bool = False) -> str:
        """Saves the uploaded file and returns an identifier for searching."""


class FileSystemStorage(AbstractStorage):
    """Local file storage on the HDD."""

    __slots__ = ('dest',)

    def __init__(
        self,
        dest: str,
        filename_strategy: t.Optional[TFilenameStrategy] = None
    ) -> None:
        super().__init__(filename_strategy)
        self.dest = os.path.expandvars(dest)

    def get_root_dir(self) -> str:
        """Returns the root directory for saving uploaded files."""
        if os.path.isabs(self.dest):
            root_dir = self.dest
        else:
            root_dir = os.path.join(
                current_app.config['UPLOADER_ROOT_DIR'],
                self.dest
            )

        if not os.path.isabs(root_dir):
            raise RuntimeError('Relative path for uploading files is not allowed.')

        if not os.access(root_dir, os.W_OK):
            raise RuntimeError(f'Not enough permissions to write to the directory {root_dir!r}.')

        return root_dir

    def load(self, lookup: str) -> File:
        return File(
            path_or_file=os.path.join(self.get_root_dir(), lookup),
            filename=os.path.basename(lookup),
            mimetype=guess_type(lookup)
        )

    def remove(self, lookup: str) -> None:
        path = os.path.join(self.get_root_dir(), lookup)

        if not os.access(path, os.W_OK):
            raise RuntimeError(f'Not enough permissions to delete the file {lookup!r}.')

        os.remove(path)

    def save(self, storage: FileStorage, overwrite: bool = False) -> str:
        root_dir = self.get_root_dir()
        lookup = self.filename_strategy(storage)
        path = os.path.join(root_dir, lookup)

        if not overwrite and os.path.exists(path):
            path = increment_path('%s_%%d%s' % os.path.splitext(path))
            lookup = os.path.relpath(path, root_dir)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        storage.save(path)

        return lookup
