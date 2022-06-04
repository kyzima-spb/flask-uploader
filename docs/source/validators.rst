.. _validators:

Валидаторы
==========

Конструктор :py:class:`~flask_uploader.core.Uploader` принимает необязательный аргумент ``validators``.
Валидатором может быть любой вызываемый объект,
который в качестве единственного аргумента принимает загруженный файл
и в случае ошибки выбрасывает исключение :py:class:`~flask_uploader.exceptions.ValidationError`:

.. code-block:: python

    # Source code from Flask-Uploader

    import typing as t

    from werkzeug.datastructures import FileStorage

    TValidator = t.Callable[[FileStorage], None]

Все встроенные валидаторы созданы на базе классов
и принимают в конструкторе необязательный аргумент ``message``,
который можно передать если вы хотите изменить сообщение об ошибке.

FileRequired
------------

:py:class:`~flask_uploader.validators.FileRequired` - проверяет, что файл был выбран и отправлен.
Если файл не выбран в HTML-форме, то Flask создает экземпляр
:py:class:`~werkzeug.datastructures.FileStorage` без имени файла,
явное приведение к логическому типу вернет ``False``.
На этой логике строится работа данного валидатора:

.. code-block:: python

    >>> from werkzeug.datastructures import FileStorage
    >>> from flask_uploader.validators import FileRequired

    >>> v = FileRequired()

    >>> f = FileStorage(name='file', filename='test.txt')
    >>> v(f)

    >>> f = FileStorage(name='file')
    >>> v(f)
    Traceback (most recent call last):
      ...
    flask_uploader.exceptions.ValidationError: The file "file" is required.

    >>> f = FileStorage(name='file', filename='')
    >>> v(f)
    Traceback (most recent call last):
      ...
    flask_uploader.exceptions.ValidationError: The file "file" is required.

Extension
---------

:py:class:`~flask_uploader.validators.Extension` - проверяет расширение файла.
Можно использовать определенные в классе константы или их сочетание, либо вручную указать нужные расширения:

.. code-block:: python

    >>> from werkzeug.datastructures import FileStorage
    >>> from flask_uploader.validators import Extension

    >>> v = Extension(Extension.IMAGES)

    >>> f = FileStorage(filename='test.jpg')
    >>> v(f)

    >>> f = FileStorage(filename='test.txt')
    >>> v(f)
    Traceback (most recent call last):
      ...
    flask_uploader.exceptions.ValidationError: This file type is not allowed to be uploaded.

    >>> v = Extension(Extension.TEXT | {'html', 'css'})
    >>> f = FileStorage(filename='test')
    >>> v(f)
    Traceback (most recent call last):
      ...
    flask_uploader.exceptions.ValidationError: The file has no extension.

    >>> v = Extension({'mp4', 'mkv'}, message='This is not a video file.')
    >>> v(f)
    Traceback (most recent call last):
      ...
    flask_uploader.exceptions.ValidationError: This is not a video file.

FileSize
--------

:py:class:`~flask_uploader.validators.FileSize` - проверяет,
что размер файла не больше и, опционально, не меньше заданного.
Размер можно указывать как количество байт целое или дробное,
либо строкой с единицой измерения (регистр значения не имеет):

* ``b`` - байты
* ``k`` или ``kb`` - килобайты
* ``m`` или ``mb`` - мегабайты
* ``g`` или ``gb`` - гигабайты
* ``t`` или ``tb`` - терабайты
* ``p`` или ``pb`` - петабайты =)

Если строка содержит не число или не верную единицу измерения, будет выброшено исключение.

.. code-block:: python

    >>> from io import BytesIO
    >>> from werkzeug.datastructures import FileStorage
    >>> from flask_uploader.validators import FileSize

    >>> f = FileStorage(BytesIO(b'abcdefg'))
    >>> v = FileSize(4)
    >>> v(f)
    Traceback (most recent call last):
      ...
    flask_uploader.exceptions.ValidationError: The size of the uploaded file must be between 0.0B and 4.0B.

    >>> f = FileStorage(BytesIO(b'abcdefg'))
    >>> v = FileSize('4b')
    >>> v(f)
    Traceback (most recent call last):
      ...
    flask_uploader.exceptions.ValidationError: The size of the uploaded file must be between 0.0B and 4.0B.

    >>> f = FileStorage()
    >>> v = FileSize(min_size=2, max_size='4b')
    >>> v(f)
    Traceback (most recent call last):
      ...
    flask_uploader.exceptions.ValidationError: The size of the uploaded file must be between 2.0B and 4.0B.

ImageSize
---------

:py:class:`~flask_uploader.validators.ImageSize` - проверяет размер изображения в пикселях.
Можно отдельно проверить минимальную или максимульную ширину или высоту,
либо любое сочетание этих параметров.
В валидаторе объявлены константы сообщений об ошибках для часто используемых вариантов проверок.
Например:

.. code-block:: python

    from flask_uploader.validators import ImageSize

    # Точный размер изображения 100x200px
    v = ImageSize(
        min_width=100, min_height=200,
        max_width=100, max_height=200,
        message=ImageSize.EXACT_SIZE,
    )

    # Изображение больше или равно 100x200px
    v = ImageSize(
        min_width=100, min_height=200,
        message=ImageSize.SIZE_GREATER_EQUAL,
    )

    # Изображение меньше или равно 1920x1080px
    v = ImageSize(
        max_width=1920, max_height=1080,
        message=ImageSize.SIZE_LESS_EQUAL,
    )

Новый валидатор
---------------

Вы можете реализовать абсолютно любой валидатор, например, проверить формат загруженного файла:

.. code-block:: python

    import json

    from flask_uploader import Uploader
    from flask_uploader.validators import ValidationError


    def is_json_file(storage: FileStorage) -> None:
        try:
            json.loads(storage.stream.read())  # Can use a lot of RAM.
            storage.stream.seek(0)
        except UnicodeDecodeError:
            raise ValidationError('This is not a JSON file.')
        except MemoryError:
            raise ValidationError('The file is too large.')


    files_uploader = Uploader(
        'files',
        FileSystemStorage(dest='files'),
        validators=[
            is_json_file,
        ],
    )

Если валидатору требуются дополнительные параметры,
то реализуйте его с помощью класса, а параметры передайте как аргументы конструктора.
Хороший тон, если ваш валидатор может принять необязательный параметр - сообщение об ошибке,
чтобы пользователь мог задать свое сообщение. Перепишем ранее рассмотренный валидатор:

.. code-block:: python

    import typing as t


    class IsJSON:
        def __init__(self, message: t.Optional[str] = None) -> None:
            self.message = message

        def __call__(self, storage: FileStorage) -> None:
            try:
                json.loads(storage.stream.read())  # Can use a lot of RAM.
                storage.stream.seek(0)
            except UnicodeDecodeError:
                raise ValidationError(
                    self.message or 'This is not a JSON file.'
                )
            except MemoryError:
                raise ValidationError(
                    self.message or 'The file is too large.'
                )
