from __future__ import annotations
from abc import ABCMeta, abstractmethod
from datetime import datetime
import os
import typing as t

from flask import current_app
from werkzeug.datastructures import FileStorage

from .formats import guess_type
from .utils import get_extension, md5stream, split_pairs


__all__ = (
    'AbstractStorage',
    'File',
    'FileSystemStorage',
    'HashedFilenameStrategy',
    'TFilenameStrategy',
    'TimestampStrategy',
)

# from werkzeug.utils import secure_filename
#
#
# def original_filename(storage: FileStorage) -> str:
#     # Non-ASCII characters will be removed
#     # For filename '天安门.jpg' returns 'jpg'
#     return secure_filename(storage.filename) if storage.filename else ''


TFilenameStrategy = t.Callable[[FileStorage], str]


class File(t.NamedTuple):
    """The result of reading a file from the selected storage."""
    path_or_file: t.Union[str, t.BinaryIO]
    lookup: t.Optional[str] = None
    filename: t.Optional[str] = None
    mimetype: t.Optional[str] = None


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


class TimestampStrategy:
    """
    The strategy uses the current timestamp as the filename.

    Can be an integer or a formatted string.
    """

    __slots__ = ('fmt', 'as_int')

    def __init__(
        self,
        fmt: str = '%Y-%m-%d-%H-%M-%S',
        as_int: bool = False
    ) -> None:
        """
        Arguments:
            fmt (str): Format string.
            as_int (bool): Name as an integer.
        """
        self.fmt = fmt
        self.as_int = as_int

    def __call__(self, storage: FileStorage) -> str:
        now = datetime.now()
        return '%s%s' % (
            int(now.timestamp()) if self.as_int else now.strftime(self.fmt),
            get_extension(storage.filename) if storage.filename else ''
        )


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
            lookup=lookup,
            path_or_file=os.path.join(self.get_root_dir(), lookup),
            filename=os.path.basename(lookup),
            mimetype=guess_type(lookup)
        )

    def remove(self, lookup: str) -> None:
        path = os.path.join(self.get_root_dir(), lookup)

        if not os.access(path, os.W_OK):
            raise RuntimeError(f'Not enough permissions to delete the file {lookup!r}.')

        os.remove(path)

    def _resolve_conflict(self, path: str) -> str:
        """
        If a file with the given path already exists in the file system,
        this method is called to resolve the conflict.
        It should return a new path for the file.

        Runs in log(n) time where n is the number of existing files in sequence.
        Author of this solution `James`_.

        .. _`James`: https://stackoverflow.com/a/47087513/10509709
        """
        path_pattern = '%s_%%d%s' % os.path.splitext(path)
        i = 1

        # First do an exponential search
        while os.path.exists(path_pattern % i):
            i = i * 2

        # Result lies somewhere in the interval (i/2..i]
        # We call this interval (a..b] and narrow it down until a + 1 = b
        a, b = (i // 2, i)

        while a + 1 < b:
            c = (a + b) // 2  # interval midpoint
            a, b = (c, b) if os.path.exists(path_pattern % c) else (a, c)

        return path_pattern % b

    def save(self, storage: FileStorage, overwrite: bool = False) -> str:
        root_dir = self.get_root_dir()
        lookup = self.filename_strategy(storage)
        path = os.path.join(root_dir, lookup)

        if not overwrite and os.path.exists(path):
            path = self._resolve_conflict(path)
            lookup = os.path.relpath(path, root_dir)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        storage.save(path)

        return lookup


def iter_files(storage: FileSystemStorage) -> t.Iterable[File]:
    """
    Returns an iterator over all files in the given file system storage.

    This function cannot be used in a production environment
    because it returns all files without any filtering.
    This can lead to memory leaks and freezes.
    """
    upload_dir = storage.get_root_dir()

    for root, dirs, files in os.walk(upload_dir):
        for f in files:
            path = os.path.abspath(os.path.join(root, f))
            lookup = os.path.relpath(path, upload_dir)
            yield File(
                lookup=lookup,
                path_or_file=path,
                filename=os.path.basename(lookup),
                mimetype=guess_type(lookup, use_external=True)
            )
