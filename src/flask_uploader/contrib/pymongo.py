import typing as t

from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
from gridfs import GridFSBucket
from werkzeug.datastructures import FileStorage

from ..exceptions import (
    FileNotFound,
    InvalidLookup,
    MultipleFilesFound,
)
from ..storages import (
    AbstractStorage,
    File,
    TFilenameStrategy,
)
from ..formats import guess_type


__all__ = (
    'GridFSStorage',
    'Lookup',
)


class Lookup(str):
    def __init__(self, value: t.Union[str, ObjectId]) -> None:
        if not isinstance(value, ObjectId):
            try:
                value = ObjectId(value)
            except InvalidId as err:
                raise InvalidLookup(str(err)) from err
        self.value = value


class GridFSStorage(AbstractStorage):
    """File storage in the MongoDB database."""

    __slots__ = ('mongo', 'collection')

    def __init__(
        self,
        mongo: PyMongo,
        collection: str,
        filename_strategy: t.Optional[TFilenameStrategy] = None
    ) -> None:
        """
        Arguments
            mongo (PyMongo): A instance of the extension of Flask-Pymongo.
            collection (str): The MongoDB collection in which files are saved.
        """
        super().__init__(filename_strategy=filename_strategy)
        self.mongo = mongo
        self.collection = collection

    def get_bucket(self) -> GridFSBucket:
        """Returns an object for working with GridFS."""
        return GridFSBucket(self.mongo.db, self.collection)

    def iter_files(self) -> t.Iterable[File]:
        for grid_out in self.get_bucket().find():
            yield File(
                lookup=Lookup(grid_out._id),
                path_or_file=t.cast(t.BinaryIO, grid_out),
                filename=grid_out.filename,
                mimetype=grid_out.metadata['contentType'],
            )

    def load(self, lookup: t.Union[str, ObjectId]) -> File:
        bucket = self.get_bucket()
        lookup = Lookup(lookup)
        grid_out = bucket.open_download_stream(lookup.value)

        if grid_out is None:
            raise FileNotFound(
                f'File with lookup {lookup!r} not found '
                f'in GridFS collection {self.collection!r}.'
            )

        return File(
            lookup=lookup,
            path_or_file=t.cast(t.BinaryIO, grid_out),
            filename=grid_out.filename,
            mimetype=grid_out.content_type,
        )

    def remove(self, lookup: t.Union[str, ObjectId]) -> None:
        self.get_bucket().delete(Lookup(lookup).value)

    def save(self, storage: FileStorage, overwrite: bool = False) -> Lookup:
        bucket = self.get_bucket()
        filename = self.filename_strategy(storage)
        content_type = guess_type(filename, use_external=True)

        if overwrite:
            result = list(bucket.find({'filename': filename}).limit(2))
            found = len(result)

            if found > 1:
                raise MultipleFilesFound(
                    'Multiple files were found. Overwriting is not possible.'
                )

            if found:
                lookup = Lookup(result[0]._id)
                bucket.delete(lookup.value)
                bucket.upload_from_stream_with_id(
                    lookup.value,
                    filename,
                    storage.stream,
                    metadata={'contentType': content_type}
                )
                return lookup

        return Lookup(bucket.upload_from_stream(
            filename,
            storage.stream,
            metadata={'contentType': content_type}
        ))
