__all__ = (
    'UploaderException',
    'FileNotFound',
    'InvalidLookup',
    'ValidationError',
    'UploadNotAllowed',
)


class UploaderException(Exception):
    pass


class FileNotFound(UploaderException):
    """The file was not found in the storage."""


class InvalidLookup(UploaderException):
    """
    Incorrect format of a unique identifier
    used to search for a file in the storage.
    """


class ValidationError(UploaderException):
    """An error when validation of the file."""


UploadNotAllowed = ValidationError
