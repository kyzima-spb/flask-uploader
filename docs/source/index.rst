.. _index:


Flask-Uploader
==============

|PyPI| |LICENCE| |STARS| |DOCS|

**Flask-Uploader** - загрузчик файлов для Flask с гибкой возможностью расширения.

Быстрый старт
=============

Установка
---------

Установите последнюю стабильную версию, выполнив команду::

    pip install flask-uploader

Или установите последнюю тестовую версию, которая может и будет содержать баги =)
Она автоматически собирается и публикуется на `test.pypi.org`_::

    pip install \
        --extra-index-url=https://test.pypi.org/simple \
        flask-uploader


Конфигурация
------------

Это расширение использует для инициализации функцию :py:func:`~flask_uploader.init_uploader`
(правилами разработки расширений для Flask это допустимо).
Вызывать эту фукнцию допустимо в любом месте, обычно это:

* фабричная функция, которая возвращает экземлпяр приложения (предпочтительный вариант)
* модуль с экземплярами всех используемых расширений
* модуль, в котором вы создаете экземпляр приложения (худший вариант)

.. code-block:: python

    # Module that contains a factory function

    from flask import Flask
    from flask_uploader import init_uploader


    def create_app():
        app = Flask(__name__, instance_relative_config=True)
        # Reading and setting configuration options
        init_uploader(app)
        # Initializing everything you need
        return app

Следующие конфигурационные опции доступны для установки:

=========================================    ================================================================
Опция                                        Описание
=========================================    ================================================================
`UPLOADER_ROOT_DIR`                          Корневая директория для загруженных файлов.
                                             Должна существовать и иметь права на запись.
                                             По-умолчанию ``''``, но обязателен для
                                             :py:class:`~flask_uploader.storages.FileSystemStorage`.
`UPLOADER_BLUEPRINT_NAME`                    Программное имя, используемое внутренним Blueprint.
                                             По-умолчанию ``_uploader``.
`UPLOADER_BLUEPRINT_URL_PREFIX`              URL префикс, используемый внутренним Blueprint.
                                             По-умолчанию ``/media``.
`UPLOADER_BLUEPRINT_SUBDOMAIN`               Имя поддомена, используемое внутренним Blueprint.
                                             По-умолчанию ``None``.
`UPLOADER_DEFAULT_ENDPOINT`                  Имя входной точки для доступа к загруженному файлу,
                                             используемое внутренним Blueprint.
                                             По-умолчанию ``download``.
=========================================    ================================================================

Создание загрузчика
-------------------

**Загрузчик** - это экземпляр класса :py:class:`~flask_uploader.Uploader`.
**Цели загрузчика**:

* валидация загруженного файла
* сохранение загруженного файла в хранилище
* чтение файла из хранилища по уникальному идентификатору
* удаление файла из хранилища по уникальному идентификатору
* получение URL-адреса для доступа к загруженному файлу

В первом аргументе конструктора нужно передать **уникальное имя**.
Это имя используется :ref:`в маршруте по-умолчанию <Маршруты по-умолчанию>`
и :ref:`для получения ранее созданного экземпляра загрузчика <Поиск загрузчика>`.

Во втором аргументе конструктора необходимо передать экземпляр выбранного хранилища.

Остальные аргументы конструктора являются не обязательными, однако помните,
что первое правило разработчика - "не доверять пользователю", поэтому любые входные данные должны быть отвалидированы.

По-умолчанию именованный аргумент ``validators`` конструктора пустой.
Это означает, что загрузчик разрешает любой файл.
Обязательно передайте значение этого аргумента в зависимости от вашей задачи.

В примере мы создаем загрузчик с именем ``images``,
который будет сохранять загруженные файлы на жестком диске относительно корня директории,
заданной конфигурационной опцией ``UPLOADER_ROOT_DIR``.
Разрешены только файлы изображений, для всех остальных файлов будет выброшено исключение
:py:class:`~flask_uploader.validators.ValidationError`.

.. code-block:: python

    # Module with endpoint handlers, for example - routes/photos.py

    from flask_uploader import Uploader
    from flask_uploader import validators
    from flask_uploader.storages import FileSystemStorage


    images_uploader = Uploader(
        'images',
        FileSystemStorage(dest='.'),
        validators=[
            validators.ExtensionValidator(
                validators.ExtensionValidator.IMAGES
            ),
        ]
    )

Маршруты по-умолчанию
~~~~~~~~~~~~~~~~~~~~~

``Flask-Uploader`` создает экземпляр :py:class:`~flask.Blueprint`
для регистрации обработчиков конечных точек по-умолчанию:

* ``/<name>/<path:lookup>`` - маршрут для доступа к загруженному файлу,
  где ``name`` это уникальное имя загрузчика, а ``lookup`` - уникальный идентификатор файла.
  В примере с фотографиями, загруженный файл будет доступен для скачивания по адресу::

      http://127.0.0.1:5000/media/photos/<lookup>

Поиск загрузчика
~~~~~~~~~~~~~~~~

Экземпляр загрузчика можно создать в любом удобном для вас месте,
а затем в обработчике входной точки получить ранее созданный экземпляр с помощью статического метода
:py:meth:`~flask_uploader.UploaderMeta.get_instance`:

.. code-block:: python

    from flask_uploader import Uploader

    images_uploader = Uploader.get_instance('images')

Входная точка
-------------

Дополним наш пример обработчиком входной точки для загрузки изображений:

.. code-block:: python

    # Continuation of the routes/photos.py module

    from flask import Blueprint, flash, redirect, request


    bp = Blueprint('photos', __name__, url_prefix='/photos')


    @bp.route('/', methods=['POST'])
    def upload():
        if 'file' not in request.files:
            flash('No file part.')
            return redirect(request.url)

        try:
            photos_uploader.save(request.files['file'], overwrite=True)
            flash('File saved successfully.')
        except validators.ValidationError as err:
            flash(str(err))

        return redirect(request.url)


.. |PyPI| image:: https://img.shields.io/pypi/v/flask-uploader.svg
   :target: https://pypi.org/project/flask-uploader/
   :alt: Latest Version

.. |LICENCE| image:: https://img.shields.io/github/license/kyzima-spb/flask-uploader.svg
   :target: https://github.com/kyzima-spb/flask-uploader/blob/master/LICENSE
   :alt: MIT

.. |STARS| image:: https://img.shields.io/github/stars/kyzima-spb/flask-uploader.svg
   :target: https://github.com/kyzima-spb/flask-uploader/stargazers

.. |DOCS| image:: https://readthedocs.org/projects/flask-uploader/badge/?version=latest
   :target: https://flask-uploader.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. _test.pypi.org: https://test.pypi.org/project/flask-uploader/
