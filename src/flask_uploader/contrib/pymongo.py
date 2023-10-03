from __future__ import annotations
import os
import re
import typing as t

from bson.errors import InvalidId
from bson.objectid import ObjectId
from gridfs import GridFSBucket
from gridfs.errors import NoFile
from pymongo import ASCENDING, DESCENDING

from ..exceptions import FileNotFound, InvalidLookup
from ..formats import guess_type
from ..storages import AbstractStorage, File

if t.TYPE_CHECKING:
    from flask_pymongo import PyMongo
    from gridfs.grid_file import GridOut
    from pymongo.client_session import ClientSession
    from werkzeug.datastructures import FileStorage
    from ..typing import FilenameStrategyCallable


__all__ = ('GridFSStorage', 'Lookup')


class Bucket(GridFSBucket):
    def delete_file(
        self,
        filename: str,
        session: t.Optional[ClientSession] = None,
    ) -> None:
        """Removes all versions of a file with the given name."""
        cursor = (
            self.find({'filename': filename})
                .sort('uploadDate', ASCENDING)
        )
        for grid_out in cursor:
            self.delete(grid_out._id, session=session)

    def find_last_version(
        self,
        filename: str,
        session: t.Optional[ClientSession] = None,
    ) -> t.Optional[GridOut]:
        """
        Returns the last uploaded version
        of the file with the given name or None.
        """
        try:
            return self.open_download_stream_by_name(
                filename, revision=-1, session=session
            )
        except NoFile:
            return None

    def get_last_index(self, file_pattern: str) -> int:
        """
        Returns the last index found
        for the given filename pattern, otherwise 0.
        """
        file_pattern = re.escape(file_pattern).replace('%d', r'(\d+)')

        try:
            found = next(
                self.find({'filename': {'$regex': file_pattern}})
                    .sort('metadata.index', DESCENDING)
                    .limit(1)
            )
            return int(found.metadata['index'])
        except StopIteration:
            return 0


class Lookup(str):
    """
    A search identifier that is both a string and stores a native identifier.
    """

    def __init__(self, value: str) -> None:
        self._oid: t.Optional[ObjectId] = None

    def __repr__(self) -> str:
        return '<{} filename={!r} oid={!r}>'.format(
            self.__class__.__name__, str(self), self.oid
        )

    @property
    def oid(self) -> t.Optional[ObjectId]:
        return self._oid

    @oid.setter
    def oid(self, value: t.Union[str, ObjectId]) -> None:
        if not isinstance(value, ObjectId):
            try:
                value = ObjectId(value)
            except InvalidId as err:
                raise InvalidLookup(str(err)) from err
        self._oid = value


class GridFSStorage(AbstractStorage):
    """File storage in the MongoDB database."""

    __slots__ = ('mongo', 'collection')

    def __init__(
        self,
        mongo: PyMongo,
        collection: str,
        filename_strategy: t.Optional[FilenameStrategyCallable] = None,
    ) -> None:
        """
        Arguments
            mongo (PyMongo): A instance of the extension of Flask-Pymongo.
            collection (str): The MongoDB collection in which files are saved.
        """
        super().__init__(filename_strategy=filename_strategy)
        self.mongo = mongo
        self.collection = collection

    def _resolve_conflict(self, filename: str) -> t.Tuple[str, int]:
        """
        If a file with the name already exists in the GridFS,
        this method is called to resolve the conflict.
        It should return a new filename and index.
        """
        filename_pattern = '%s_%%d%s' % os.path.splitext(filename)
        index = self.get_bucket().get_last_index(filename_pattern) + 1
        return filename_pattern % index, index

    def get_bucket(self) -> Bucket:
        """Returns an object for working with GridFS."""
        return Bucket(self.mongo.db, self.collection)

    def load(self, lookup: str) -> File:
        bucket = self.get_bucket()
        grid_out = bucket.find_last_version(lookup)

        if grid_out is None:
            raise FileNotFound(
                f'File with lookup {lookup!r} not found '
                f'in GridFS collection {self.collection!r}.'
            )

        return File(
            lookup=lookup,
            path_or_file=t.cast(t.BinaryIO, grid_out),
            filename=os.path.basename(grid_out.filename),
            mimetype=grid_out.metadata['contentType'],  # type: ignore
        )

    def remove(self, lookup: str) -> None:
        self.get_bucket().delete_file(lookup)

    def save(self, storage: FileStorage, overwrite: bool = False) -> Lookup:
        bucket = self.get_bucket()
        filename = self.generate_filename(storage)
        metadata: t.Dict[str, t.Any] = {
            'contentType': (
                guess_type(filename, use_external=True) or storage.mimetype,
            )
        }
        found = bucket.find_last_version(filename)

        if found and overwrite:
            if found.metadata is not None:
                metadata.update()

            lookup = Lookup(filename)
            lookup.oid = found._id

            bucket.delete(found._id)
            bucket.upload_from_stream_with_id(
                file_id=found._id,
                filename=filename,
                source=storage.stream,
                metadata=metadata,
            )

            return lookup

        if found and not overwrite:
            filename, metadata['index'] = self._resolve_conflict(filename)

        lookup = Lookup(filename)
        lookup.oid = bucket.upload_from_stream(
            filename,
            storage.stream,
            metadata=metadata,
        )

        return lookup


def iter_files(storage: GridFSStorage) -> t.Iterable[File]:
    """
    Returns an iterator over all files in the given GridFS storage.

    This function cannot be used in a production environment
    because it returns all files without any filtering.
    This can lead to memory leaks and freezes.
    """
    for grid_out in storage.get_bucket().find():
        yield File(
            lookup=grid_out.filename,
            path_or_file=t.cast(t.BinaryIO, grid_out),
            filename=os.path.basename(grid_out.filename),
            mimetype=grid_out.metadata['contentType'],
        )
