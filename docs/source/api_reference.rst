.. _api_reference:

API Reference
=============

Core Reference
--------------

.. autofunction:: flask_uploader.init_uploader

.. autoclass:: flask_uploader.core.UploaderMeta
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.core.Uploader
    :members:
    :undoc-members:
    :show-inheritance:

Exceptions Reference
--------------------

.. autoclass:: flask_uploader.exceptions.UploaderException
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.exceptions.FileNotFound
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.exceptions.InvalidLookup
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.exceptions.MultipleFilesFound
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.exceptions.PermissionDenied
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.exceptions.ValidationError
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.exceptions.UploadNotAllowed
    :members:
    :undoc-members:
    :show-inheritance:

Formats Reference
-----------------

.. autofunction:: flask_uploader.formats.get_format
.. autofunction:: flask_uploader.formats.guess_type

.. autoclass:: flask_uploader.formats.FileFormat
    :members:
    :undoc-members:
    :show-inheritance:

Storage Reference
-----------------

.. autoclass:: flask_uploader.storages.File
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.storages.AbstractStorage
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.storages.FileSystemStorage
    :members:
    :undoc-members:
    :show-inheritance:

Strategies Reference
~~~~~~~~~~~~~~~~~~~~

.. autofunction:: flask_uploader.storages.iter_files

.. autoclass:: flask_uploader.storages.TFilenameStrategy
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.storages.HashedFilenameStrategy
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.storages.TimestampStrategy
    :members:
    :undoc-members:
    :show-inheritance:

Utils Reference
---------------

.. autofunction:: flask_uploader.utils.get_extension
.. autofunction:: flask_uploader.utils.md5file
.. autofunction:: flask_uploader.utils.md5stream
.. autofunction:: flask_uploader.utils.split_pairs

Validators Reference
--------------------

.. autoclass:: flask_uploader.validators.Extension
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.validators.FileRequired
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.validators.FileSize
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.validators.ImageSize
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.validators.TValidator
    :members:
    :undoc-members:
    :show-inheritance:

Views Reference
---------------

.. autoclass:: flask_uploader.views.BaseView
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.views.DestroyView
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.views.DownloadView
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.views.UploaderMixin
    :members:
    :undoc-members:
    :show-inheritance:

Contrib Reference
-----------------

GridFS Reference
~~~~~~~~~~~~~~~~

.. autofunction:: flask_uploader.contrib.pymongo.iter_files

.. autoclass:: flask_uploader.contrib.pymongo.Bucket
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.pymongo.Lookup
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.pymongo.GridFSStorage
    :members:
    :undoc-members:
    :show-inheritance:

Amazon Reference
~~~~~~~~~~~~~~~~

.. autofunction:: flask_uploader.contrib.aws.iter_files
.. autofunction:: flask_uploader.contrib.aws.catch_client_error

.. autoclass:: flask_uploader.contrib.aws.AWS
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.aws.S3Storage
    :members:
    :undoc-members:
    :show-inheritance:

WTForms Reference
~~~~~~~~~~~~~~~~~

.. autofunction:: flask_uploader.contrib.wtf.file_is_selected
.. autofunction:: flask_uploader.contrib.wtf.wrap_validator

.. autoclass:: flask_uploader.contrib.wtf.UploadField
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.wtf.Extension
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.wtf.extension
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.wtf.FileSize
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.wtf.file_size
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.wtf.ImageSize
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.wtf.image_size
    :members:
    :undoc-members:
    :show-inheritance:
