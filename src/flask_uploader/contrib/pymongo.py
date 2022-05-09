import typing as t

from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
from gridfs import GridFS
from werkzeug.datastructures import FileStorage

from ..exceptions import FileNotFound, InvalidLookup
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

    def get_fs(self) -> GridFS:
        """Returns an object for working with GridFS."""
        return GridFS(self.mongo.db, self.collection)

    def load(self, lookup: t.Union[str, ObjectId]) -> File:
        fs = self.get_fs()
        grid_out = fs.find_one({'_id': Lookup(lookup).value})

        if grid_out is None:
            raise FileNotFound(
                f'File with lookup {lookup!r} not found '
                f'in GridFS collection {self.collection!r}.'
            )

        return File(
            path_or_file=t.cast(t.BinaryIO, grid_out),
            filename=grid_out.filename,
            mimetype=grid_out.content_type,
        )

    def remove(self, lookup: t.Union[str, ObjectId]) -> None:
        self.get_fs().delete(Lookup(lookup).value)

    def save(self, storage: FileStorage, overwrite: bool = False) -> Lookup:
        fs = self.get_fs()
        filename = self.filename_strategy(storage)
        kwargs = {
            'filename': filename,
            'content_type': guess_type(filename, use_external=True),
        }

        if overwrite:
            grid_out = fs.find_one(
                {'filename': filename}, sort=[('uploadDate', 1)]
            )

            if grid_out is not None:
                fs.delete(grid_out._id)
                kwargs['_id'] = grid_out._id

        return Lookup(fs.put(storage.stream, **kwargs))
