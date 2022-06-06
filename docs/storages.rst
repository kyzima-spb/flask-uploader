.. _storages:

Хранилища
=========

Файловая система
----------------

Самый часто используемый тип хранилища, не требующий установки дополнительных зависимостей.
Конструктор :py:class:`~flask_uploader.storages.FileSystemStorage`
принимает один обязательный аргумент ``dest`` - путь к директории,
в которой будут сохраняться загруженные файлы.
Значение может быть:

* абсолютным путем;
* относительным путем с обязательной опцией ``UPLOADER_ROOT_DIR``,
  тогда абсолютный путь рассчитывается как ``{UPLOADER_ROOT_DIR}/{dest}``;
* относительным путем с включенной опцией ``UPLOADER_INSTANCE_RELATIVE_ROOT``,
  тогда абсолютный путь рассчитывается как ``<instance_folder>/{dest}``;
* относительным путем с включенной опцией ``UPLOADER_INSTANCE_RELATIVE_ROOT``
  и не пустым значением опции ``UPLOADER_ROOT_DIR``,
  тогда абсолютный путь рассчитывается как ``<instance_folder>/{UPLOADER_ROOT_DIR}/{dest}``.

Пример №1:

.. code-block:: python

    >>> from flask import Flask
    >>> from flask_uploader.storages import FileSystemStorage

    >>> app = Flask(__name__)
    >>> app.config['UPLOADER_ROOT_DIR'] = '/app/uploads/'

    >>> files_storage = FileSystemStorage(dest='files')
    >>> files_storage.get_root_dir()
    '/app/uploads/files'

Пример №2:

.. code-block:: python

    >>> from flask import Flask
    >>> from flask_uploader.storages import FileSystemStorage

    >>> app = Flask(__name__, instance_path='/app/instance') # for example
    >>> app.config['UPLOADER_ROOT_DIR'] = 'uploads'
    >>> app.config['UPLOADER_INSTANCE_RELATIVE_ROOT'] = True

    >>> files_storage = FileSystemStorage(dest='files')
    >>> files_storage.get_root_dir()
    '/app/instance/uploads/files'

Рекомендуется избегать общих директорий для разных экземпляров хранилищ,
Это защитит вас от случайной перезаписи, удаления или несанкционированного доступа к файлам
другими загрузчиками или хранилищами. Например::

    uploads
    └── files
        ├── books
        └── photos

.. code-block:: python

    from flask import Flask
    from flask_uploader.storages import FileSystemStorage

    # Good practice
    books_storage = FileSystemStorage(dest='files/books')
    photos_storage = FileSystemStorage(dest='files/photos')

    # Bad practice, has access to files from other storages.
    files_storage = FileSystemStorage(dest='files')

MongoDB GridFS
--------------

Из документации:

    **GridFS** - это спецификация для хранения и извлечения файлов,
    размер которых превышает предельный размер документа BSON равный 16Mb.

``Flask-Uploader`` использует расширение `Flask-Pymongo`_,
поэтому все доступные конфигурационные параметры смотрите в их документации.

Чтобы использовать GridFS неоходимо установить дополнительные зависимости::

    pip install 'Flask-Uploader[pymongo]'

Затем создайте новый экземпляр хранилища на основе класса
:py:class:`~flask_uploader.contrib.pymongo.GridFSStorage`.
Конструктор принимает два обязательных аргумента:
экземпляр расширения :py:class:`~flask_pymongo.PyMongo`
и имя коллекции для сохранения файлов:

.. code-block:: python

    from flask_pymongo import PyMongo
    from flask_uploader.contrib.pymongo import GridFSStorage

    mongo = PyMongo()
    books_storage = GridFSStorage(mongo, 'books')

Рекомендуется использовать разные коллекции для разных экземпляров хранилищ.
Это защитит вас от случайной перезаписи, удаления или несанкционированного доступа к файлам
другими загрузчиками или хранилищами.

Перезапись файла
~~~~~~~~~~~~~~~~

Из документации:

    Не используйте GridFS, если вам нужно обновить содержимое всего файла атомарно.
    В качестве альтернативы вы можете хранить несколько версий каждого файла
    и указывать текущую версию в метаданных после загрузки новой версии файла,
    а затем, при необходимости, удалить предыдущие версии.

``GridFSStorage`` не использует версионирование.
Если метод :py:meth:`~flask_uploader.contrib.pymongo.GridFSStorage.save`
вызывается с аргументом ``overwrite`` равным ``False``, то для файла генерируется новое имя.
Если метод :py:meth:`~flask_uploader.contrib.pymongo.GridFSStorage.save`
вызывается с аргументом ``overwrite`` равным ``True``, то существующий файл удаляется
и создается новый с точно таким же первичным ключом.

ObjectId
~~~~~~~~

Метод :py:meth:`~flask_uploader.contrib.pymongo.GridFSStorage.save` возвращает не обычную строку,
а специальный тип :py:class:`~flask_uploader.contrib.pymongo.Lookup`, унаследованный от :py:class:`str`.

Чтобы получить идентификатор сохраненного файла, обратитесь к свойству ``oid``:

.. code-block:: python

    lookup = books_uploader.save(request.files['file'], overwrite=True)
    mongo.db.books.insert_one({
        'title': request.form['title'],
        'file': lookup.oid,
    })

Amazon S3
---------

``Flask-Uploader`` использует официальный SDK Boto3_ и реализует встроенное расширение Flask-AWS:
:py:class:`~flask_uploader.contrib.aws.AWS`.
Вы можете использовать любой облачный сервис, совместимый с API Amazon, например Yandex.Cloud.

Следующие конфигурационные опции сессии доступны для установки:

=========================================    ================================================================
Опция                                        Описание
=========================================    ================================================================
`AWS_ACCESS_KEY_ID`                          Идентификатор ключа доступа AWS.
                                             По-умолчанию ``None``, но обязателен в большинстве случаев.
`AWS_SECRET_ACCESS_KEY`                      Секретный ключ доступа AWS.
                                             По-умолчанию ``None``, но обязателен в большинстве случаев.
`AWS_AWS_SESSION_TOKEN`                      Временный токен сеанса AWS.
                                             По-умолчанию ``None``.
`AWS_REGION_NAME`                            Регион по умолчанию при создании новых подключений.
                                             По-умолчанию ``None``.
`AWS_PROFILE_NAME`                           Имя используемого профиля.
                                             Если не задан, используется профиль по умолчанию.
                                             По-умолчанию ``None``.
=========================================    ================================================================

Следующие конфигурационные опции доступны для низкоуровневых клиентов, либо для ресурсов.

Значения опций можно задавать глобально для всех клиентов и ресурсов,
тогда имена опций совпадают с именами, указанными в таблице ниже.

Либо указать опцию для конкретного сервиса, например облачного хранилища ``S3``,
тогда имена опций указываются по шаблону: ``AWS_<service_name>_<option_name>``,
например ``AWS_S3_ENDPOINT_URL``:

=========================================    ================================================================
Опция                                        Описание
=========================================    ================================================================
`AWS_API_VERSION`                            Используемая версия API.
                                             По умолчанию используется последняя версия.
                                             Вам нужно указать этот параметр только в том случае,
                                             если вы хотите использовать предыдущую версию API.
                                             По-умолчанию ``None``.
`AWS_USE_SSL`                                Использовать SSL или нет.
                                             По умолчанию используется SSL.
                                             Обратите внимание,
                                             что не все сервисы поддерживают подключения без SSL.
                                             По-умолчанию ``True``.
`AWS_VERIFY`                                 Проверять или нет SSL-сертификаты.
                                             По умолчанию SSL-сертификаты проверяются.
                                             По-умолчанию ``None``.
`AWS_ENDPOINT_URL`                           Полный URL-адрес (включая схему ``http/https``),
                                             используемый созданным клиентом или ресурсом для подключения.
                                             Если указан, то ``AWS_USE_SSL`` игнорируется.
                                             По-умолчанию ``None``.
=========================================    ================================================================

Чтобы использовать облачное хранишище S3 неоходимо установить дополнительные зависимости::

    pip install 'Flask-Uploader[aws]'

Затем создайте новый экземпляр хранилища на основе класса
:py:class:`~flask_uploader.contrib.aws.S3Storage`.
Конструктор принимает два обязательных аргумента:
экземпляр ресурса ``S3``, который можно создать с помощью метода расширения
:py:meth:`~flask_uploader.contrib.aws.AWS.resource`
и имя корзины для сохранения файлов:

.. code-block:: python

    from flask_uploader.contrib.aws import AWS, S3Storage

    aws = AWS()
    storage = S3Storage(
        aws.resource('s3'),
        'flask-uploader',
    )

Если вы хотите использовать одну корзину для разных экземпляров
:py:class:`~flask_uploader.contrib.aws.S3Storage`,
то рекомендуется задать уникальный префикс для ключей
и избегать более общих префиксов для разных экземпляров хранилищ,
Это защитит вас от случайной перезаписи, удаления или несанкционированного доступа к файлам
другими загрузчиками или хранилищами:

.. code-block:: python

    from flask_uploader.contrib.aws import AWS, S3Storage

    aws = AWS()
    storage = S3Storage(
        aws.resource('s3'),
        'flask-uploader',
        key_prefix='files',
    )

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

    from uuid import uuid4

    from werkzeug.datastructures import FileStorage


    def uuid_strategy(storage: FileStorage) -> str:
        return str(uuid4())

В момент создания экземпляра хранилища в конструктор передайте аргумент ``filename_strategy``:

.. code-block:: python

    from flask_uploader.storages import FileSystemStorage

    storage = FileSystemStorage(
        dest='files',
        filename_strategy=uuid_strategy
    )

Метод :py:meth:`~flask_uploader.storages.AbstractStorage.save` перед сохранением проверит:

1. что сгенерированное имя не пустая строка, иначе выбросит исключение
   :py:class:`~flask_uploader.exceptions.InvalidLookup`;
2. что сгенерированное имя имеет расширение, иначе добавит его автоматически;
3. что файл существует и если явно не передан аргумент ``overwrite``,
   добавит к имени суффикс ``_N`` (изменить суффикс нельзя).

Это верно для любой стратегии.


.. _Flask-Pymongo: https://flask-pymongo.readthedocs.io/en/latest/
.. _Boto3: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
