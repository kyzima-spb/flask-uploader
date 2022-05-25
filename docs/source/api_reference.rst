.. _api_reference:

API Reference
=============

Core Reference
--------------

.. autofunction:: flask_uploader.init_uploader

.. autoclass:: flask_uploader.core.UploaderMeta
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.core.Uploader
    :members:
    :show-inheritance:

Exceptions Reference
--------------------

.. autoclass:: flask_uploader.exceptions.UploaderException
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.exceptions.FileNotFound
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.exceptions.InvalidLookup
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.exceptions.MultipleFilesFound
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.exceptions.ValidationError
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.exceptions.UploadNotAllowed
    :members:
    :show-inheritance:

Storage Reference
-----------------

.. autoclass:: flask_uploader.storages.File
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.storages.TFilenameStrategy
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.storages.HashedFilenameStrategy
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.storages.AbstractStorage
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.storages.FileSystemStorage
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.pymongo.GridFSStorage
    :members:
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
    :show-inheritance:

.. autoclass:: flask_uploader.validators.FileRequired
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.validators.FileSize
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.validators.ImageSize
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.validators.MimeType
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.validators.TValidator
    :members:
    :show-inheritance:

Views Reference
---------------

.. autoclass:: flask_uploader.views.BaseView
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.views.DestroyView
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.views.DownloadView
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.views.UploaderMixin
    :members:
    :show-inheritance:

Contrib Reference
-----------------

GridFS Reference
~~~~~~~~~~~~~~~~

.. autofunction:: flask_uploader.contrib.pymongo.iter_files

.. autoclass:: flask_uploader.contrib.pymongo.Bucket
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.pymongo.Lookup
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.pymongo.GridFSStorage
    :members:
    :show-inheritance:

Amazon Reference
~~~~~~~~~~~~~~~~

.. autofunction:: flask_uploader.contrib.aws.iter_files
.. autofunction:: flask_uploader.contrib.aws.catch_client_error

.. autoclass:: flask_uploader.contrib.aws.AWS
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.aws.S3Storage
    :members:
    :show-inheritance:

WTForms Reference
~~~~~~~~~~~~~~~~~

.. autofunction:: flask_uploader.contrib.wtf.file_is_selected
.. autofunction:: flask_uploader.contrib.wtf.wrap_validator

.. autoclass:: flask_uploader.contrib.wtf.UploaderField
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.wtf.Extension
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.wtf.extension
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.wtf.FileSize
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.wtf.file_size
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.wtf.ImageSize
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.wtf.image_size
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.wtf.MimeType
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.wtf.mime_type
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.contrib.wtf.UploaderField
    :members:
    :show-inheritance:
