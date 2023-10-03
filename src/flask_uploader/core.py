from __future__ import annotations
import typing as t
import weakref

from flask import (
    current_app,
    url_for,
)

if t.TYPE_CHECKING:
    from werkzeug.datastructures import FileStorage
    from .storages import AbstractStorage, File
    from .typing import ValidatorCallable

    Cache = weakref.WeakValueDictionary[str, 'Uploader']


__all__ = (
    'Uploader',
)


class UploaderMeta(type):
    """
    File uploader metaclass.

    Caches instances under the unique name passed
    in the first argument to the constructor
    and prevents instantiation of uploaders with the existing name.
    """
    def __init__(
        cls,
        name: str,
        bases: t.Tuple[type, ...],
        d: t.Dict[str, t.Any],
    ) -> None:
        super().__init__(name, bases, d)

        if not hasattr(cls, '_cache'):
            cls._cache: Cache = weakref.WeakValueDictionary()

    def __call__(
        cls,
        name: str,
        storage: AbstractStorage,
        validators: t.Optional[t.Sequence[ValidatorCallable]] = None,
        endpoint: t.Optional[str] = None,
        use_auto_route: bool = True,
    ) -> Uploader:
        if name in cls._cache:
            raise RuntimeError(f'Uploader with name {name!r} already exists.')

        if endpoint is not None:
            use_auto_route = False

        obj: Uploader = super().__call__(  # without obj lost reference
            name,
            storage,
            validators=validators,
            endpoint=endpoint,
            use_auto_route=use_auto_route,
        )
        cls._cache[name] = obj

        return obj

    def get_instance(cls, name: str) -> Uploader:
        """Returns the uploader instance by unique name."""
        if name not in cls._cache:
            raise RuntimeError(f'Uploader with name {name!r} not found.')
        return cls._cache[name]


class Uploader(metaclass=UploaderMeta):
    """File uploader with the ability to select different types of storage."""

    __slots__ = (
        '__weakref__',
        'name',
        '_storage',
        'validators',
        '_endpoint',
        'use_auto_route',
    )

    def __init__(
        self,
        name: str,
        storage: AbstractStorage,
        validators: t.Optional[t.Sequence[ValidatorCallable]] = None,
        endpoint: t.Optional[str] = None,
        use_auto_route: bool = True,
    ) -> None:
        """
        Arguments:
            name (str):
                The unique name of the uploader.
            storage (AbstractStorage):
                Storage instance for file manipulation.
            validators (ValidatorCallable):
                List of called objects for validating the uploaded file.
            endpoint (str):
                The name of the endpoint to generate the URL.
            use_auto_route (bool):
                Allows downloading a file at the default URL.
        """
        if validators is None:
            validators = []

        self.name = name
        self._storage = storage
        self.validators = validators
        self._endpoint = endpoint
        self.use_auto_route = use_auto_route

    def __repr__(self) -> str:
        return '<{} name={!r}>'.format(
            self.__class__.__name__, self.name
        )

    def get_url(self, lookup: str, external: bool = False) -> str:
        """
        Returns the URL to the given file.

        Arguments:
            lookup (str):
                The unique identifier for the file in the selected storage.
                Usually this is the path to the file.
            external (bool):
                Generate absolute URL. Default to ``False``.
        """
        if self._endpoint is not None:
            return url_for(self._endpoint, lookup=lookup, _external=external)

        url = self._storage.get_url(lookup)

        if url is not None:
            return url

        if not self.use_auto_route:
            raise RuntimeError(
                'It is not possible to return the URL'
                ' because public access is denied.'
            )

        return url_for(
            '%s.%s' % (
                current_app.config['UPLOADER_BLUEPRINT_NAME'],
                current_app.config['UPLOADER_DEFAULT_ENDPOINT'],
            ),
            name=self.name,
            lookup=lookup,
            _external=external
        )

    def load(self, lookup: str) -> File:
        """Reads and returns a ``File`` object for an identifier."""
        return self._storage.load(lookup)

    def remove(self, lookup: str) -> None:
        """Deletes a file from storage by unique identifier."""
        self._storage.remove(lookup)

    def save(
        self,
        storage: FileStorage,
        overwrite: bool = False,
        skip_validation: bool = False,
    ) -> str:
        """
        Saves the uploaded file and returns an identifier for searching.

        Arguments:
            storage (FileStorage):
                Object to represent uploaded file.
            overwrite (bool):
                Overwrite existing file. Default to ``False``.
            skip_validation (bool):
                Do not validate the uploaded file. Default to ``False``.
        """
        if not skip_validation:
            self.validate(storage)
        return self._storage.save(storage, overwrite=overwrite)

    def validate(self, storage: FileStorage) -> None:
        """
        Validates the uploaded file and throws a
        :py:class`~flask_uploader.exceptions.ValidationError`
        exception if an error appears.
        """
        for validator in self.validators:
            validator(storage)
