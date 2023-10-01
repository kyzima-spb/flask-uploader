from __future__ import annotations
import inspect
import typing as t
from urllib.parse import urlparse

from flask import (
    abort,
    current_app,
    redirect,
    request,
    send_file as _send_file,
)
from flask.views import MethodView

from .core import Uploader
from .exceptions import FileNotFound
from .storages import File

if t.TYPE_CHECKING:
    from flask.typing import ResponseReturnValue


__all__ = (
    'BaseView',
    'DestroyView',
    'DownloadView',
    'UploaderMixin',
)


class UploaderMixin:
    """
    The mixin adds the uploader_or_name property,
    whose value is the uploader instance or its unique name,
    and the get_uploader method, which returns the uploader instance.
    """
    uploader_or_name: t.Optional[t.Union[str, Uploader]] = None

    def get_uploader(self) -> Uploader:
        """Returns the uploader instance."""
        if isinstance(self.uploader_or_name, Uploader):
            return self.uploader_or_name

        if isinstance(self.uploader_or_name, str):
            return Uploader.get_instance(self.uploader_or_name)

        raise AttributeError(
            'You must assign the value of the attribute `uploader_or_name`, '
            f'or override the `{self.__class__.__name__}.get_uploader()` '
            'method.'
        )


class BaseView(UploaderMixin, MethodView):
    """
    The base view class for endpoints that use only one uploader.
    """

    def __init__(
        self,
        uploader_or_name: t.Optional[t.Union[str, Uploader]] = None,
    ) -> None:
        if uploader_or_name is not None:
            self.uploader_or_name = uploader_or_name


class DestroyView(BaseView):
    """
    A view that handles deleting a file by unique lookup.
    """

    def get_redirect_url(self) -> str:
        """Returns the redirect URL after a delete operation."""
        redirect_url = '/'

        if request.referrer is not None:
            url = urlparse(request.referrer)
            server = urlparse(request.host_url)

            if url.scheme == server.scheme and url.netloc == server.netloc:
                redirect_url = (
                    url._replace(scheme='')
                       ._replace(netloc='')
                       .geturl()
                )

        return redirect_url

    def post(self, lookup: str) -> ResponseReturnValue:
        self.get_uploader().remove(lookup)
        return redirect(self.get_redirect_url())


class DownloadView(BaseView):
    """
    The view that handles the file download.

    Used with two routes:

    * ``/<path:lookup>`` - uses the uploader returned by
      the :py:meth:`~flask_uploader.views.UploaderMixin.get_uploader` method.
      Used to override the default view.
    * ``/<name>/<path:lookup>`` - uses the uploader returned by
      the static method
      :py:meth:`~flask_uploader.core.UploaderMeta.get_instance`.
      Used as the default view.
    """

    def send_file(self, f: File) -> ResponseReturnValue:
        """Send the contents of a given file to the client."""
        kwargs = {}
        sig = inspect.signature(_send_file)

        if 'download_name' in sig.parameters:
            kwargs['download_name'] = f.filename
        else:
            kwargs['attachment_filename'] = f.filename

        return _send_file(
            f.path_or_file,
            mimetype=f.mimetype,
            as_attachment=True,
            **kwargs,  # type: ignore
        )

    def get(
        self,
        lookup: str,
        name: t.Optional[str] = None,
    ) -> ResponseReturnValue:
        if name is None:
            uploader = self.get_uploader()
        else:
            uploader = Uploader.get_instance(name)
            if not uploader.use_auto_route:
                abort(404)

        try:
            return self.send_file(uploader.load(lookup))
        except FileNotFound as err:
            current_app.logger.info(str(err))
            abort(404)
