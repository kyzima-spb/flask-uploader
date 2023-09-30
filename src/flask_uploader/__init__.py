from __future__ import annotations
try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version
import typing as t

from flask import Blueprint

from .core import Uploader
from .views import DownloadView

if t.TYPE_CHECKING:
    from flask import Flask


__all__ = (
    'init_uploader',
    'Uploader',
)
__version__ = version(__package__)


def init_uploader(app: Flask) -> None:
    app.config.setdefault('UPLOADER_ROOT_DIR', '')
    app.config.setdefault('UPLOADER_INSTANCE_RELATIVE_ROOT', False)
    app.config.setdefault('UPLOADER_BLUEPRINT_NAME', '_uploader')
    app.config.setdefault('UPLOADER_BLUEPRINT_URL_PREFIX', '/media')
    app.config.setdefault('UPLOADER_BLUEPRINT_SUBDOMAIN', None)
    app.config.setdefault('UPLOADER_DEFAULT_ENDPOINT', 'download')

    @app.context_processor
    def processors() -> t.Dict[str, t.Any]:
        def media_url(name: str, lookup: str) -> str:
            return Uploader.get_instance(name).get_url(lookup)
        return dict(media_url=media_url)

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
