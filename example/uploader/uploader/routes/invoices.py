from flask import (
    Blueprint,
    flash,
    render_template,
    redirect,
    request,
)
from flask_login import login_required
from flask_uploader import Uploader
from flask_uploader.exceptions import UploadNotAllowed
from flask_uploader.storages import (
    FileSystemStorage,
    iter_files,
    TimestampStrategy
)
from flask_uploader.validators import Extension
from flask_uploader.views import (
    BaseView,
    DestroyView,
    DownloadView,
)


bp = Blueprint('invoices', __name__, url_prefix='/invoices')

invoices_storage = FileSystemStorage(dest='invoices', filename_strategy=TimestampStrategy())
invoices_uploader = Uploader(
    'invoices',
    invoices_storage,
    endpoint='site.invoices.download',
    validators=[
        Extension(
            Extension.OFFICE
        ),
    ]
)


class DeleteInvoiceView(DestroyView):
    decorators = [login_required]
    uploader_or_name = invoices_uploader


class DownloadInvoiceView(DownloadView):
    decorators = [login_required]
    uploader_or_name = invoices_uploader


class UploadInvoiceView(BaseView):
    decorators = [login_required]
    uploader_or_name = invoices_uploader

    def get(self):
        return render_template('invoices.html', files=iter_files(invoices_storage))

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


download_endpoint = DownloadInvoiceView.as_view('download')
upload_endpoint = UploadInvoiceView.as_view('index')
delete_endpoint = DeleteInvoiceView.as_view('remove')

bp.add_url_rule('/', view_func=upload_endpoint)
bp.add_url_rule('/<path:lookup>', view_func=download_endpoint)
bp.add_url_rule('/remove/<path:lookup>', view_func=delete_endpoint)
