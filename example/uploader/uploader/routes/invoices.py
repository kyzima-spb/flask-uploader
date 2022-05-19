from flask import (
    Blueprint,
    flash,
    render_template,
    redirect,
    request,
)
from flask_uploader import Uploader
from flask_uploader.exceptions import UploadNotAllowed
from flask_uploader.storages import FileSystemStorage, iter_files
from flask_uploader.validators import MimeTypeValidator
from flask_uploader.views import (
    BaseView,
    DestroyView,
    DownloadView,
)


bp = Blueprint('invoices', __name__, url_prefix='/invoices')

invoices_uploader = Uploader(
    'invoices',
    FileSystemStorage(dest='invoices'),
    endpoint='site.invoices.download',
    validators=[
        MimeTypeValidator(
            MimeTypeValidator.OFFICE
        ),
    ]
)


class UploaderView(BaseView):
    uploader_or_name = invoices_uploader

    def get(self):
        return render_template(
            'invoices.html',
            files=iter_files(invoices_uploader.storage),
            uploader=invoices_uploader,
        )

    def post(self):
        if 'file' not in request.files:
            flash('No file part.')
            return redirect(request.url)

        try:
            uploader = self.get_uploader()
            print(request.files['file'].mimetype)
            lookup = uploader.save(request.files['file'], overwrite=True)
            flash(f'Invoice saved successfully - {lookup}.')
        except UploadNotAllowed as err:
            flash(str(err))

        return redirect(request.url)


uploader_endpoint = UploaderView.as_view('index')
download_endpoint = DownloadView.as_view('download', uploader_or_name=invoices_uploader)
delete_endpoint = DestroyView.as_view('remove', uploader_or_name=invoices_uploader)

bp.add_url_rule('/', view_func=uploader_endpoint)
bp.add_url_rule('/<path:lookup>', view_func=download_endpoint)
bp.add_url_rule('/remove/<path:lookup>', view_func=delete_endpoint)
