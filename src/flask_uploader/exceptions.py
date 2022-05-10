__all__ = (
    'UploaderException',
    'FileNotFound',
    'InvalidLookup',
    'MultipleFilesFound',
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


class MultipleFilesFound(UploaderException):
    """
    There are multiple files in the storage with the same name,
    including the prefix, if any.
    """


class ValidationError(UploaderException):
    """An error when validation of the file."""


UploadNotAllowed = ValidationError
