from __future__ import annotations
import typing as t
import weakref

from flask import (
    abort,
    Blueprint,
    current_app,
    Flask,
    send_file,
    url_for,
)
from flask.views import MethodView
from flask.typing import ResponseReturnValue
from werkzeug.datastructures import FileStorage

from .storages import AbstractStorage, File
from .validators import TValidator
from .utils import md5stream, split_pairs


__all__ = (
    'DownloadView',
    'init_uploader',
    'Uploader',
)


Cache = weakref.WeakValueDictionary[str, 'Uploader']


class UploaderMeta(type):
    """
    File uploader metaclass.

    Caches instances under the unique name passed in the first argument to the constructor
    and prevents instantiation of uploaders with the existing name.
    """
    def __init__(
        cls,
        name: str,
        bases: tuple[type, ...],
        d: dict[str, t.Any]
    ) -> None:
        super().__init__(name, bases, d)

        if not hasattr(cls, '_cache'):
            cls._cache: Cache = weakref.WeakValueDictionary()

    def __call__( # type: ignore
        cls,
        name: str,
        storage: AbstractStorage,
        validators: t.Optional[t.Sequence[TValidator]] = None,
        endpoint: t.Optional[str] = None,
        use_auto_route: bool = True,
    ) -> Uploader:
        if name in cls._cache:
            raise RuntimeError(f'Uploader with name {name!r} already exists.')

        if endpoint is not None:
            use_auto_route = False

        obj: Uploader = super().__call__( # without obj lost reference
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
        'storage',
        'validators',
        '_endpoint',
        'use_auto_route',
    )

    def __init__(
        self,
        name: str,
        storage: AbstractStorage,
        validators: t.Optional[t.Sequence[TValidator]] = None,
        endpoint: t.Optional[str] = None,
        use_auto_route: bool = True
    ) -> None:
        """
        Arguments:
            name (str): The unique name of the uploader.
            storage (AbstractStorage): Storage instance for file manipulation.
            validators (TValidator): List of called objects for validating the uploaded file.
            endpoint (str): The name of the endpoint to generate the URL.
            use_auto_route (bool): Allows downloading a file at the default URL.
        """
        if validators is None:
            validators = []

        self.name = name
        self.storage = storage
        self.validators = validators
        self._endpoint = endpoint
        self.use_auto_route = use_auto_route

    def get_url(self, lookup: str, external: bool = True) -> str:
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

        url = self.storage.get_url(lookup)

        if url is not None:
            return url

        if not self.use_auto_route:
            raise RuntimeError(
                'It is not possible to return the URL because public access is denied.'
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
        return self.storage.load(lookup)

    def remove(self, lookup: str) -> None:
        """Deletes a file from storage by unique identifier."""
        self.storage.remove(lookup)

    def save(self, storage: FileStorage, overwrite: bool = False) -> str:
        """Saves the uploaded file and returns an identifier for searching."""
        for validator in self.validators:
            validator(storage)
        return self.storage.save(storage, overwrite=overwrite)


class DownloadView(MethodView):
    def get(self, name: str, lookup: str) -> ResponseReturnValue:
        try:
            uploader = Uploader.get_instance(name)

            if not uploader.use_auto_route:
                abort(404)

            f = uploader.load(lookup)

            return send_file(
                path_or_file=f.path_or_file,
                attachment_filename=f.filename,
                mimetype=f.mimetype,
                as_attachment=True,
            )
        except RuntimeError:
            abort(404)


def init_uploader(app: Flask) -> None:
    app.config.setdefault('UPLOADER_ROOT_DIR', '')
    app.config.setdefault('UPLOADER_BLUEPRINT_NAME', '_uploader')
    app.config.setdefault('UPLOADER_BLUEPRINT_URL_PREFIX', '/media')
    app.config.setdefault('UPLOADER_BLUEPRINT_SUBDOMAIN', None)
    app.config.setdefault('UPLOADER_DEFAULT_ENDPOINT', 'download')

    bp = Blueprint(
        app.config['UPLOADER_BLUEPRINT_NAME'],
        __name__,
        url_prefix=app.config['UPLOADER_BLUEPRINT_URL_PREFIX'],
        subdomain=app.config['UPLOADER_BLUEPRINT_SUBDOMAIN']
    )
    bp.add_url_rule(
        '/<name>/<path:lookup>',
        view_func=DownloadView.as_view(app.config['UPLOADER_DEFAULT_ENDPOINT'])
    )
    app.register_blueprint(bp)
