.. _validators:

Валидаторы
==========

Валидатором может быть любой вызываемый объект,
который в качестве единственного аргумента принимает загруженный файл
и в случае ошибки выбрасывает исключение :py:class:`~flask_uploader.validators.ValidationError`:

.. code-block:: python

    # Source code from Flask-Uploader

    import typing as t

    from werkzeug.datastructures import FileStorage

    TValidator = t.Callable[[FileStorage], None]

Новый валидатор
---------------

Вы можете реализовать абсолютно любой валидатор, например, обязательный выбор файла
(если файл не выбран в HTML-форме, то Flask создает пустой файл без имени):

.. code-block:: python

    from flask_uploader.validators import ValidationError
    from werkzeug.datastructures import FileStorage

    def required(storage: FileStorage) -> None:
        if not storage.filename:
            raise ValidationError('File not selected.')

В момент создания экземпляра загрузчика в конструктор передайте аргумент ``validators``:

.. code-block:: python

    from flask_uploader import Uploader
    from flask_uploader.validators import ExtensionValidator


    files_uploader = Uploader(
        'files',
        FileSystemStorage(dest='files'),
        validators=[
            required,
        ]
    )

Если валидатору требуется передать дополнительные параметры, то реализуйте класс:

.. code-block:: python

    from flask_uploader import Uploader
    from flask_uploader.validators import MimeTypeValidator
    from PIL import Image
    from werkzeug.datastructures import FileStorage


    class ImageSizeValidator:
        def __init__(self, width: int, height: int) -> None:
            self.width = width
            self.height = height

        def __call__(self, storage: FileStorage) -> None:
            image = Image.open(storage.stream)
            width, height = image.size
            storage.stream.seek(0)

            if self.width < width or self.height < height:
                raise ValidationError(
                    'The image size is larger than %dx%d.' % (
                        self.width, self.height
                    )
                )

    photos_uploader = Uploader(
        'photos',
        FileSystemStorage(dest='photos'),
        validators=[
            MimeTypeValidator(MimeTypeValidator.IMAGES),
            ImageSizeValidator(1024, 1024),
        ]
    )
