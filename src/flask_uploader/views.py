from __future__ import annotations
import typing as t

from flask import (
    abort,
    current_app,
    send_file,
)
from flask.views import MethodView
from flask.typing import ResponseReturnValue

from .core import Uploader
from .exceptions import FileNotFound, InvalidLookup


__all__ = (
    'DownloadView',
)


# class UploaderMixin:
#     uploader_or_name: t.Optional[str] = None
#
#     def get_uploader(self):
#         pass


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
        except (FileNotFound, InvalidLookup) as err:
            msg = str(err) if current_app.debug else None
            abort(404, msg)
