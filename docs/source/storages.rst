.. _storages:

Хранилища
=========

Имя файла
---------

Оригинальное имя загруженного файла не используется при сохранении.
Новое имя должна вернуть **стратегия** - это вызываемый объект,
который в качестве единственного аргумента принимает загруженный файл и возвращает новое имя.

.. code-block:: python

    # Source code from Flask-Uploader

    import typing as t

    from werkzeug.datastructures import FileStorage

    TFilenameStrategy = t.Callable[[FileStorage], str]

По-умолчанию используется :py:class:`~flask_uploader.storages.HashedFilenameStrategy`,
которая генерирует имя, вычисляя хэш содержимого файла и разбивая его на указанное количество частей указанной длины.
Она решает проблему хранения большого количества файлов на жестком диске,
когда количество файлов в одном каталоге ограничено ОС.
Благодаря хешу и разбиению файлы равномерно хранятся в каталогах.

Новая стратегия
~~~~~~~~~~~~~~~

Вы можете реализовать абсолютно любую стратегию для генерации имени,
например, пусть имя сохраняемого файла будет текущей датой и временем:

.. code-block:: python

    from datetime import datetime

    from flask_uploader.utils import get_extension
    from werkzeug.datastructures import FileStorage


    def timestamp_strategy(storage: FileStorage) -> str:
        return '%s%s' % (
            datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
            get_extension(storage.filename) if storage.filename else ''
        )

В момент создания экземпляра хранилища в конструктор передайте аргумент ``filename_strategy``:

.. code-block:: python

    from flask_uploader.storages import FileSystemStorage

    storage = FileSystemStorage(
        dest='files',
        filename_strategy=timestamp_strategy
    )

Если все таки нужно сохранить оригинальное имя, то можно реализовать такую стратегию:

.. code-block:: python

    from werkzeug.utils import secure_filename

    def original_filename(storage: FileStorage) -> str:
        # Non-ASCII characters will be removed
        # For filename '天安门.jpg' returns 'jpg'
        if storage.filename:
            return secure_filename(storage.filename)
        return ''

Помните, что метод :py:meth:`~flask_uploader.storages.AbstractStorage.save` перед сохранением
проверит существование файла, если явно не передан аргумент ``overwrite``,
и если файл существует, то к имени будет добавлен постфикс.
Это верно для любой стратегии.
