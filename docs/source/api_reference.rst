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

.. autoclass:: flask_uploader.validators.ValidationError
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.validators.TValidator
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.validators.ExtensionValidator
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.validators.MimeTypeValidator
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
