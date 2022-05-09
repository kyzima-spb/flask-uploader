.. _api_reference:

API Reference
=============

Core
----

.. autofunction:: flask_uploader.init_uploader

.. autoclass:: flask_uploader.UploaderMeta
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.Uploader
    :members:
    :show-inheritance:

.. autoclass:: flask_uploader.DownloadView
    :members:
    :show-inheritance:

Storages
--------

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

Validators
----------

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

Utils
-----

.. autofunction:: flask_uploader.utils.get_extension
.. autofunction:: flask_uploader.utils.md5file
.. autofunction:: flask_uploader.utils.md5stream
.. autofunction:: flask_uploader.utils.split_pairs
