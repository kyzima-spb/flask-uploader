.. _index:


Flask-Uploader
==============

|PyPI| |LICENCE| |STARS| |DOCS|

|DOWNLOADS| |DOWNLOADS_M| |DOWNLOADS_W|

Document version: |version| |release|

**Flask-Uploader** - загрузчик файлов для Flask с гибкой возможностью расширения.

Быстрый старт
=============

Установка
---------

Установите последнюю стабильную версию, выполнив команду::

    pip install Flask-Uploader

Или установите последнюю тестовую версию, которая может и будет содержать баги =)
Она автоматически собирается и публикуется на `test.pypi.org`_::

    pip install \
        -i https://test.pypi.org/simple/ \
        -i https://pypi.python.org/simple \
            Flask-Uploader

Конфигурация
------------

``Flask-Uploader`` использует для инициализации функцию :py:func:`~flask_uploader.init_uploader`
(это разрешено `правилами разработки расширений`_ для Flask).
Вызвать эту фукнцию можно в любом месте, обычно это:

* `фабричная функция`_, которая возвращает экземпляр приложения (предпочтительный вариант)
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
                                             По-умолчанию ``''``, но обязательна для
                                             :py:class:`~flask_uploader.storages.FileSystemStorage`.
`UPLOADER_INSTANCE_RELATIVE_ROOT`            Если истина, то ``UPLOADER_ROOT_DIR`` может быть задан
                                             как относительный путь от корня директории экземпляра.
                                             По-умолчанию ``False``.
`UPLOADER_BLUEPRINT_NAME`                    Программное имя, используемое
                                             :ref:`внутренним Blueprint <Доступ к файлу>`.
                                             По-умолчанию ``_uploader``.
`UPLOADER_BLUEPRINT_URL_PREFIX`              URL префикс, используемый
                                             :ref:`внутренним Blueprint <Доступ к файлу>`.
                                             По-умолчанию ``/media``.
`UPLOADER_BLUEPRINT_SUBDOMAIN`               Имя поддомена, используемое
                                             :ref:`внутренним Blueprint <Доступ к файлу>`.
                                             По-умолчанию ``None``.
`UPLOADER_DEFAULT_ENDPOINT`                  Имя входной точки для доступа к загруженному файлу,
                                             используемое
                                             :ref:`внутренним Blueprint <Доступ к файлу>`.
                                             По-умолчанию ``download``.
=========================================    ================================================================

Создание загрузчика
-------------------

**Загрузчик** - это экземпляр класса :py:class:`~flask_uploader.core.Uploader`.
**Цели загрузчика**:

* валидация загруженного файла
* сохранение загруженного файла в хранилище
* чтение файла из хранилища по уникальному идентификатору
* удаление файла из хранилища по уникальному идентификатору
* получение URL-адреса для доступа к загруженному файлу

В первом аргументе конструктора нужно передать **уникальное имя**.
Это имя используется :ref:`в маршруте по-умолчанию <Маршруты по-умолчанию>`
и :ref:`для получения ранее созданного экземпляра загрузчика <Поиск загрузчика>`.

Во втором аргументе конструктора необходимо передать экземпляр :ref:`выбранного хранилища <storages>`.

Остальные аргументы конструктора являются необязательными, однако помните,
что первое правило разработчика - `"не доверять пользователю"`,
поэтому любые входные данные должны быть :ref:`отвалидированы <validators>`.

По-умолчанию именованный аргумент ``validators`` конструктора пустой.
Это означает, что загрузчик разрешает любой файл.
Обязательно передайте значение этого аргумента в зависимости от вашей задачи.

В примере мы создаем загрузчик с именем ``photos``,
который будет сохранять загруженные файлы на жестком диске относительно корня директории,
заданной конфигурационной опцией ``UPLOADER_ROOT_DIR`` в поддиректории ``photos``.
Разрешены только файлы изображений не более 10Mb и размером 1920х1080px,
для всех остальных файлов будет выброшено исключение
:py:class:`~flask_uploader.validators.ValidationError`.

.. code-block:: python

    # Module with endpoint handlers, for example - routes/photos.py

    from flask_uploader import Uploader
    from flask_uploader.storages import FileSystemStorage
    from flask_uploader.validators import (
        Extension,
        ImageSize,
        FileRequired,
        FileSize,
    )


    photos_storage = FileSystemStorage(dest='photos')
    photos_uploader = Uploader(
        'photos',
        photos_storage,
        validators=[
            FileRequired(),
            FileSize('10Mb'),
            Extension(Extension.IMAGES),
            ImageSize(max_width=1920, max_height=1080),
        ]
    )

Поиск загрузчика
~~~~~~~~~~~~~~~~

Экземпляр загрузчика можно создать в любом удобном для вас месте,
а затем в обработчике входной точки получить ранее созданный экземпляр с помощью статического метода
:py:meth:`~flask_uploader.core.UploaderMeta.get_instance`:

.. code-block:: python

    from flask_uploader import Uploader

    photos_uploader = Uploader.get_instance('photos')

Входная точка
-------------

Дополним наш пример обработчиком входной точки для загрузки изображений:

.. code-block:: python

    # Continuation of the routes/photos.py module

    from flask import Blueprint, flash, redirect, request
    from flask_uploader.exceptions import UploadNotAllowed


    bp = Blueprint('photos', __name__, url_prefix='/photos')


    @bp.route('/', methods=['POST'])
    def upload():
        if 'file' not in request.files:
            flash('No file part.')
            return redirect(request.url)

        try:
            lookup = photos_uploader.save(request.files['file'])
            flash(f'Photo saved successfully - {lookup}.')
        except UploadNotAllowed as err:
            flash(str(err))

        return redirect(request.url)

Доступ к файлу
--------------

``Flask-Uploader`` создает экземпляр :py:class:`~flask.Blueprint`
для регистрации обработчиков конечных точек по-умолчанию.

Доступ по-умолчанию
~~~~~~~~~~~~~~~~~~~

``/<name>/<path:lookup>`` - маршрут по-умолчанию для доступа к загруженному файлу,
где ``name`` это уникальное имя загрузчика, а ``lookup`` - уникальный идентификатор файла,
используемый для поиска в :ref:`выбранном хранилище <storages>`.
В примере с фотографиями, загруженный файл будет доступен для скачивания по адресу::

    http://127.0.0.1:5000/media/photos/<lookup>

**lookup** - имеет строковой тип даных, в большинстве случаев это относительный путь к файлу,
поэтому в маршруте используется URL-конвертер :py:class:`~werkzeug.routing.PathConverter`.

Запрет доступа
~~~~~~~~~~~~~~

Если вам нужно запретить публичный доступ к загруженным файлам для маршрута по-умолчанию,
то в момент создания экземпляра :py:class:`~flask_uploader.core.Uploader` в конструктор
передайте аргумент ``use_auto_route`` со значением ``False``:

.. code-block:: python

    # Module with endpoint handlers, for example - routes/payments.py

    from flask_uploader import Uploader
    from flask_uploader.storages import FileSystemStorage
    from flask_uploader.validators import Extension


    payments_uploader = Uploader(
        'payments',
        FileSystemStorage(dest='payments'),
        use_auto_route=False,
        validators=[
            Extension(
                Extension.IMAGES | Extension.EDOCUMENTS
            ),
        ]
    )

Контроль доступа
~~~~~~~~~~~~~~~~

Доступ к загруженному файлу можно контролировать, это может быть полезно в следующих случаях:

* нужно изменить публичный URL-адрес
* запретить доступ для неаутентифицированных пользователей
* использовать промежуточное ПО или HTTP-сервер для обслуживания файлов

Для этого в момент создания экземпляра :py:class:`~flask_uploader.core.Uploader` в конструктор
передайте аргумент ``endpoint`` с именем конечной точки, включая имена всех Blueprint.
Используйте представление :py:class:`~flask_uploader.views.DownloadView`
для описания конечной точки:

.. code-block:: python

    # Module with endpoint handlers, for example - routes/invoices.py

    from flask import Blueprint
    from flask_login import login_required
    from flask_uploader import Uploader
    from flask_uploader.storages import FileSystemStorage
    from flask_uploader.validators import Extension
    from flask_uploader.views import DownloadView


    bp = Blueprint('invoices', __name__, url_prefix='/invoices')

    invoices_storage = FileSystemStorage(dest='invoices')
    invoices_uploader = Uploader(
        'invoices',
        invoices_storage,
        endpoint='invoices.download',
        validators=[
            Extension(
                Extension.OFFICE
            ),
        ]
    )


    class DownloadInvoiceView(DownloadView):
        decorators = [login_required]
        uploader_or_name = invoices_uploader


    download_endpoint = DownloadInvoiceView.as_view('download')

    bp.add_url_rule('/<path:lookup>', view_func=download_endpoint)

Промежуточное ПО
~~~~~~~~~~~~~~~~

Чтобы отдать загруженные файлы, используя промежуточное ПО, например Nginx_,
в конфигурационном файле вирутального хоста определите новое правило (``location``),
которое перекрывает маршрут по-умолчанию:

.. code-block:: nginx

    # Part of the virtual host configuration file

    client_max_body_size 100m;

    location /media/photos/ {
        rewrite ^/media/(.*)$ /$1 break;
        root /path/to/uploader_root_dir;
    }

Удаление файла
--------------

По-умолчанию удаление файла недоступно, это сделано из соображений безопасности.
Используйте представление :py:class:`~flask_uploader.views.DestroyView`
для описания конечной точки:

.. code-block:: python

    # Continuation of the routes/invoices.py module

    from flask_uploader.views import DownloadView


    class DeleteInvoiceView(DestroyView):
        decorators = [login_required]
        uploader_or_name = invoices_uploader


    delete_endpoint = DeleteInvoiceView.as_view('remove')

    bp.add_url_rule('/remove/<path:lookup>', view_func=delete_endpoint)


.. |PyPI| image:: https://img.shields.io/pypi/v/flask-uploader.svg
   :target: https://pypi.org/project/flask-uploader/
   :alt: Latest Version

.. |LICENCE| image:: https://img.shields.io/github/license/kyzima-spb/flask-uploader.svg
   :target: https://github.com/kyzima-spb/flask-uploader/blob/master/LICENSE
   :alt: MIT

.. |STARS| image:: https://img.shields.io/github/stars/kyzima-spb/flask-uploader.svg
   :target: https://github.com/kyzima-spb/flask-uploader/stargazers
   :alt: GitHub stars

.. |DOCS| image:: https://readthedocs.org/projects/flask-uploader/badge/?version=latest
   :target: https://flask-uploader.readthedocs.io/ru/latest/?badge=latest
   :alt: Documentation Status

.. |DOWNLOADS| image:: https://pepy.tech/badge/flask-uploader
   :target: https://pepy.tech/project/flask-uploader

.. |DOWNLOADS_M| image:: https://pepy.tech/badge/flask-uploader/month
   :target: https://pepy.tech/project/flask-uploader)

.. |DOWNLOADS_W| image:: https://pepy.tech/badge/flask-uploader/week
   :target: https://pepy.tech/project/flask-uploader)

.. _test.pypi.org: https://test.pypi.org/project/flask-uploader/
.. _правилами разработки расширений: https://flask.palletsprojects.com/en/2.1.x/extensiondev/#initializing-extensions
.. _фабричная функция: https://flask.palletsprojects.com/en/2.1.x/patterns/appfactories/
.. _Nginx: https://nginx.org
