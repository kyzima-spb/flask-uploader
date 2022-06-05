from __future__ import annotations
from dataclasses import dataclass, field, fields
import base64
import typing as t

from bson.objectid import ObjectId, InvalidId
from flask_login import UserMixin
from flask_pymongo import PyMongo
from flask_uploader.contrib.pymongo import Lookup


_TModel = t.TypeVar('_TModel', bound='Model')


mongo = PyMongo()


@dataclass
class Model:
    def as_dict(self) -> t.Dict[str, t.Any]:
        return {
            fld.name: getattr(self, fld.name)
            for fld in fields(self) if not fld.name.startswith('_')
        }

    def get_id(self):
        try:
            return self._id
        except AttributeError:
            print('My method')
            raise NotImplementedError('No `_id` attribute - override `get_id`') from None


class Manager(t.Generic[_TModel]):
    def __init__(
        self,
        model_class: t.Type[_TModel],
        collection: t.Optional[str] = None,
    ) -> None:
        self.model_class = model_class

        if collection is None:
            collection = model_class.__name__.lower()

        self.collection = collection

    def find(self, **criteria) -> t.Iterator[_TModel]:
        for result in mongo.db[self.collection].find(criteria):
            result = self.model_class(**result)
            yield result

    def find_one(self, **criteria):
        result = mongo.db[self.collection].find_one(criteria)

        if result is not None:
            result = self.model_class(**result)

        return result

    def get(self, pk: t.Union[str, ObjectId]) -> t.Optional[_TModel]:
        try:
            result = self.find(_id=ObjectId(pk))
            return next(result, None)
        except InvalidId:
            return None

    def save(self, model: _TModel) -> None:
        if model._id is None:
            model._id = (
                mongo.db[self.collection]
                    .insert_one(model.as_dict())
                    .inserted_id
            )
        else:
            mongo.db[self.collection].update_one(
                {'_id': ObjectId(model.get_id())},
                {'$set': model.as_dict()}
            )

    def delete(self, model: _TModel) -> None:
        pk = model.get_id()
        if pk is not None:
            mongo.db[self.collection].delete_one({'_id': pk})
            model._id = None


@dataclass(eq=False)
class User(UserMixin, Model):
    _id: t.Optional[ObjectId] = None
    username: str = ''
    password: str = ''
    is_active: bool = True
    firstname: str = ''
    lastname: str = ''
    avatar: str = ''

    @property
    def id(self):
        return self._id


@dataclass
class Book(Model):
    _id: t.Optional[ObjectId] = None
    title: str = ''
    cover: t.Dict[str, t.Any] = field(default_factory=dict, repr=False)
    file: t.Union[str, Lookup] = ''
    _file: str = field(init=False, repr=False)

    @property
    def cover_url(self):
        return 'data:%s;base64, %s' % (
            self.cover['contentType'],
            base64.b64encode(self.cover['content']).decode(),
        )

    def get_file(self) -> str:
        return self._file

    def set_file(self, value: t.Union[str, Lookup]) -> None:
        if isinstance(value, Lookup):
            value = str(value)
        self._file = value


Book.file = property(Book.get_file, Book.set_file)
