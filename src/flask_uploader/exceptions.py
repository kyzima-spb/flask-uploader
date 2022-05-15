__all__ = (
    'UploaderException',
    'FileNotFound',
    'InvalidLookup',
    'MultipleFilesFound',
    'PermissionDenied',
    'ValidationError',
    'UploadNotAllowed',
)


class UploaderException(Exception):
    pass


class UploadNotAllowed(UploaderException):
    """Any error that prevents the uploaded file from being saved."""


class FileNotFound(UploaderException):
    """The file was not found in the storage."""


class InvalidLookup(UploaderException):
    """
    Incorrect format of a unique identifier
    used to search for a file in the storage.
    """


class MultipleFilesFound(UploadNotAllowed):
    """
    There are multiple files in the storage with the same name,
    including the prefix, if any.
    """


class PermissionDenied(UploaderException):
    """
    The specified action cannot be performed on the storage.

    May appear in the following cases:

    * The required directory does not exist.
    * Insufficient rights to perform the action.
    * The third party service responded with an error.
    """


class ValidationError(UploadNotAllowed):
    """An error when validation of the file."""
