from __future__ import annotations
from functools import wraps
import inspect
import io
import itertools
import os
import typing as t
import urllib.parse

from boto3.session import Session
from boto3.resources.base import ServiceResource
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from flask import current_app, g
from werkzeug.datastructures import FileStorage
from werkzeug.local import LocalProxy

from ..exceptions import (
    FileNotFound,
    PermissionDenied,
)
from ..formats import guess_type
from ..storages import AbstractStorage, File
from ..utils import increment_path

if t.TYPE_CHECKING:
    from botocore.session import Session as CoreSession
    from flask import Flask
    from mypy_boto3_s3.client import S3Client
    from mypy_boto3_s3.service_resource import (
        Bucket,
        S3ServiceResource,
    )
    from ..typing import FilenameStrategyCallable


__all__ = ('AWS', 'S3Storage')


_F = t.TypeVar('_F', bound=t.Callable[..., t.Any])


def catch_client_error(
    exc_type: t.Type[BaseException] = PermissionDenied,
) -> t.Callable[[_F], _F]:
    """
    The decorator catches all client exceptions and rethrows a new exception
    with the type specified in the decorator parameter.
    """
    def decorator(func: _F) -> _F:
        @wraps(func)
        def function_wrapper(*args: t.Any, **kwargs: t.Any) -> t.Any:
            try:
                return func(*args, **kwargs)
            except ClientError as err:
                raise exc_type(str(err)) from err

        @wraps(func)
        def generator_wrapper(*args: t.Any, **kwargs: t.Any) -> t.Any:
            try:
                yield from func(*args, **kwargs)
            except ClientError as err:
                raise exc_type(str(err)) from err

        if inspect.isgeneratorfunction(func):
            return t.cast(_F, generator_wrapper)

        return t.cast(_F, function_wrapper)
    return decorator


class AWS:
    __slots__ = ('app', 'botocore_session')

    def __init__(
        self,
        app: t.Optional[Flask] = None,
        *,
        botocore_session: t.Optional[CoreSession] = None,
    ) -> None:
        self.app = app
        self.botocore_session = botocore_session

        if app is not None:
            self.init_app(app)

    def get_app(self) -> Flask:
        return self.app if self.app else current_app

    def init_app(self, app: Flask) -> None:
        app.config.setdefault('AWS_ACCESS_KEY_ID', None)
        app.config.setdefault('AWS_SECRET_ACCESS_KEY', None)
        app.config.setdefault('AWS_AWS_SESSION_TOKEN', None)
        app.config.setdefault('AWS_REGION_NAME', None)
        app.config.setdefault('AWS_PROFILE_NAME', None)
        app.config.setdefault('AWS_API_VERSION', None)
        app.config.setdefault('AWS_USE_SSL', True)
        app.config.setdefault('AWS_VERIFY', None)
        app.config.setdefault('AWS_ENDPOINT_URL', None)
        app.teardown_appcontext(self.teardown)
        # app.extensions['aws'] = self

    def _create_client(
        self,
        service_name: str,
        **user_config: t.Any,
    ) -> BaseClient:
        clients: t.Dict[str, BaseClient] = g.setdefault('boto3_clients', {})

        if service_name not in clients:
            clients[service_name] = self.session.client(
                service_name,
                **self._make_service_config(service_name, user_config)
            )

        return clients[service_name]

    def _create_resource(
        self,
        service_name: str,
        **user_config: t.Any,
    ) -> ServiceResource:
        resources: t.Dict[str, ServiceResource] = g.setdefault(
            'boto3_resources', {}
        )

        if service_name not in resources:
            resources[service_name] = self.session.resource(
                service_name,
                **self._make_service_config(service_name, user_config)
            )

        return resources[service_name]

    def _create_session(self) -> Session:
        config = self.get_app().config
        return Session(
            aws_access_key_id=config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=config['AWS_SECRET_ACCESS_KEY'],
            aws_session_token=config['AWS_AWS_SESSION_TOKEN'],
            region_name=config['AWS_REGION_NAME'],
            botocore_session=self.botocore_session,
            profile_name=config['AWS_PROFILE_NAME'],
        )

    def _make_service_config(
        self,
        service_name: str,
        user_config: t.Dict[str, t.Any],
    ) -> t.Dict[str, t.Any]:
        """Returns the configuration parameters for creating the service."""

        def get_param(
            param_name: str,
            default: t.Optional[t.Any] = None
        ) -> t.Any:
            """
            Returns the value of the configuration parameter
            with the given name for the given service.

            Arguments:
                param_name (str): The name of the configuration parameter.
                default (mixed): Default value if not set.
            """
            key = f'AWS_{service_name}_{param_name}'.upper()
            return config.get(key.upper(), default)

        config = self.get_app().config

        return {
            'aws_access_key_id': get_param('aws_access_key_id'),
            'aws_secret_access_key': get_param('aws_secret_access_key'),
            'aws_session_token': get_param('aws_session_token'),
            'region_name': get_param('region_name'),
            'api_version': get_param('api_version', config['AWS_API_VERSION']),
            'use_ssl': get_param('use_ssl', config['AWS_USE_SSL']),
            'verify': get_param('verify', config['AWS_VERIFY']),
            'endpoint_url': get_param(
                'endpoint_url', config['AWS_ENDPOINT_URL']
            ),
            **user_config,
        }

    def client(
        self,
        service_name: str,
        **user_config: t.Any,
    ) -> BaseClient:
        """
        Create a low-level service client by name.

        Arguments:
            service_name (str):
                The name of a service, e.g. 's3' or 'ec2'.
            **user_config (dict):
                Keyword arguments for the method
                :py:meth:`~boto3.session.Session.client`.

        Returns:
            botocore.client.BaseClient: Service client instance.
        """
        return t.cast(BaseClient, LocalProxy(
            lambda: self._create_client(service_name, **user_config)
        ))

    def resource(
        self,
        service_name: str,
        **user_config: t.Any,
    ) -> ServiceResource:
        """
        Create a resource service client by name.

        Arguments
            service_name (str):
                The name of a service, e.g. 's3' or 'ec2'.
            **user_config (dict):
                Keyword arguments for the method
                :py:meth:`~boto3.session.Session.resource`.

        Returns:
            boto3.resources.base.ServiceResource: Service resource instance.
        """
        return t.cast(ServiceResource, LocalProxy(
            lambda: self._create_resource(service_name, **user_config)
        ))

    @property
    def session(self) -> Session:
        """
        Returns a session instance that stores configuration state
        and allows you to create service clients and resources.
        """
        if not hasattr(g, 'boto3_session'):
            g.boto3_session = self._create_session()
        return t.cast(Session, g.boto3_session)

    def teardown(self, exception: t.Optional[BaseException] = None) -> None:
        services = itertools.chain(
            g.get('boto3_clients', {}).items(),
            g.get('boto3_resources', {}).items(),
        )

        for name, srv in services:
            if hasattr(srv, 'close') and callable(srv.close):
                srv.close()


class S3Storage(AbstractStorage):
    __slots__ = (
        '_bucket_name',
        'is_public',
        'key_prefix',
        '_s3',
        '_url_pattern',
        'url_expires_in',
    )

    def __init__(
        self,
        s3: S3ServiceResource,
        bucket_name: str,
        key_prefix: t.Optional[str] = None,
        is_public: bool = True,
        url_expires_in: int = 3600,
        filename_strategy: t.Optional[FilenameStrategyCallable] = None,
    ) -> None:
        """
        Arguments:
            s3 (boto3.resources.base.ServiceResource):
                A resource instance for working with S3 object storage.
            bucket_name (str):
                The name of the bucket in S3 object storage.
            key_prefix (str):
                Prefix for all object keys in S3 storage (subdirectory).
            is_public (bool):
                Access to the bucket and objects is allowed for all users.
            url_expires_in (int):
                The number of seconds that signed URLs are valid.
            filename_strategy (FilenameStrategyCallable):
                A callable that returns the name of the file to save.
        """
        super().__init__(filename_strategy=filename_strategy)
        self._s3 = s3
        self._bucket_name = bucket_name
        self.is_public = is_public
        self.url_expires_in = url_expires_in
        self._url_pattern = ''

        if key_prefix is not None:
            key_prefix = key_prefix.strip('./') + '/'

        self.key_prefix = key_prefix

    def _generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Returns a public URL with a limited lifetime.

        Arguments:
            key (str): Resource ID in S3 object storage.
            expires_in (int): The lifetime of the URL in seconds.
        """
        return self.get_client().generate_presigned_url(
            'get_object',
            ExpiresIn=expires_in,
            Params={
                'Bucket': self._bucket_name, 'Key': key,
            },
        )

    def _make_key(self, lookup: str) -> str:
        """Returns the identifier of a resource in S3 object storage."""
        if self.key_prefix is None:
            return lookup
        return f'{self.key_prefix}{lookup}'

    def _make_lookup(self, key: str) -> str:
        """Returns a lookup derived from a resource ID in S3 object storage."""
        if self.key_prefix is None:
            return key

        if key.startswith(self.key_prefix):
            return key[len(self.key_prefix):]

        return key

    def _object_exists(self, key: str) -> bool:
        """
        Returns true if a file with the given key exists in S3 object storage,
        false otherwise.
        """
        try:
            self.get_bucket().Object(key).load()
            return True
        except ClientError:
            return False

    @catch_client_error()
    def _resolve_conflict(self, key: str) -> str:
        """
        If a file with the key already exists in the S3 storage,
        this method is called to resolve the conflict.
        It should return a new key for the file.
        """
        prefix, _ = os.path.splitext(key)
        objects = self.get_bucket().objects.filter(Prefix=prefix)
        return increment_path(key, (obj.key for obj in objects))

    def get_bucket(self) -> Bucket:
        """
        Returns a resource for working with a bucket in S3 object storage.
        """
        return self.get_resource().Bucket(self._bucket_name)

    def get_client(self) -> S3Client:
        """
        Returns a low level client instance for working with S3 object storage.
        """
        return self.get_resource().meta.client

    def get_resource(self) -> S3ServiceResource:
        """
        Returns a resource instance for working with S3 object storage.
        """
        if isinstance(self._s3, LocalProxy):
            return self._s3._get_current_object()
        return self._s3

    def get_url(self, lookup: str) -> str:
        """
        Returns the URL address of an object in S3 object storage.
        """
        key = self._make_key(lookup)
        if self.is_public:
            return self.get_url_pattern().format(
                key=urllib.parse.quote(key)
            )
        return self._generate_presigned_url(key, self.url_expires_in)

    def get_url_pattern(self) -> str:
        """
        Returns the public URL pattern computed programmatically.
        """
        if not self._url_pattern:
            nbsp = '\xa0'
            url = self._generate_presigned_url(nbsp, 0)
            url = urllib.parse.urlparse(url)._replace(query='').geturl()
            url = urllib.parse.unquote(url)
            self._url_pattern = url.replace(nbsp, '{key}')
        return self._url_pattern

    @catch_client_error(FileNotFound)
    def load(self, lookup: str) -> File:
        bucket = self.get_bucket()
        obj = bucket.Object(self._make_key(lookup))

        file_obj = io.BytesIO()
        obj.download_fileobj(file_obj)
        file_obj.seek(0)

        return File(
            lookup=lookup,
            path_or_file=file_obj,
            filename=os.path.basename(obj.key),
            mimetype=obj.content_type,
        )

    @catch_client_error()
    def remove(self, lookup: str) -> None:
        key = self._make_key(lookup)
        self.get_bucket().Object(key).delete()

    @catch_client_error()
    def save(self, storage: FileStorage, overwrite: bool = False) -> str:
        bucket = self.get_bucket()
        key = self._make_key(
            self.generate_filename(storage)
        )

        if not overwrite and self._object_exists(key):
            key = self._resolve_conflict(key)

        content_type = guess_type(key, use_external=True) or storage.mimetype

        bucket.put_object(
            Key=key,
            Body=storage.stream,
            ContentType=content_type,
        )

        return self._make_lookup(key)


@catch_client_error()
def iter_files(storage: S3Storage) -> t.Iterable[File]:
    """
    Returns an iterator over all files in the given S3 storage.

    This function cannot be used in a production environment!
    """
    q = storage.get_bucket().objects

    if storage.key_prefix is None:
        objects = q.all()
    else:
        objects = q.filter(Prefix=storage.key_prefix)

    for obj in objects:
        yield File(
            lookup=storage._make_lookup(obj.key),
            path_or_file=storage.get_url(obj.key),
            filename=os.path.basename(obj.key),
            mimetype=getattr(
                obj,
                'content_type',
                guess_type(obj.key, use_external=True)
            )
        )
