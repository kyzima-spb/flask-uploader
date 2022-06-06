.. migrate:

Переход с Flask-Uploads
=======================

**Flask-Uploader** является более функциональной и гибкой альтернативой
для известного в узких кругах `Flask-Uploads`_.
Этот раздел поможет вам мигрировать на ``Flask-Uploader``.

1. UploadSet
------------

В ``Flask-Uploads`` мы создаем :py:class:`~flask_uploads.UploadSet`
для валидации загруженного файла по расширению и для сохранения его на жестком диске.
Пример взят из документации к `Flask-Uploads`_:

.. code-block:: python

    from flask_uploads import UploadSet, IMAGES

    photos = UploadSet('photos', IMAGES)

В ``Flask-Uploader`` нужно создать загрузчик и хранилище:

.. code-block:: python

    from flask_uploader import Uploader
    from flask_uploader.storages import FileSystemStorage
    from flask_uploader.validators import ExtensionValidator


    photos = Uploader(
        'photos',
        FileSystemStorage(dest='photos'),
        validators=[
            ExtensionValidator(
                ExtensionValidator.IMAGES
            ),
        ]
    )

2. Входная точка
----------------

Пример взят из документации к `Flask-Uploads`_:

.. code-block:: python

    @app.route('/upload', methods=['GET', 'POST'])
    def upload():
        if request.method == 'POST' and 'photo' in request.files:
            filename = photos.save(request.files['photo'])
            rec = Photo(filename=filename, user=g.user.id)
            rec.store()
            flash('Photo saved.')
            return redirect(url_for('show', id=rec.id))
        return render_template('upload.html')

    @app.route('/photo/<id>')
    def show(id):
        photo = Photo.load(id)
        if photo is None:
            abort(404)
        url = photos.url(photo.filename)
        return render_template('show.html', url=url, photo=photo)

Вот так этот пример может быть переписан с использованием ``Flask-Uploader``:

.. code-block:: python

    @app.route('/upload', methods=['GET', 'POST'])
    def upload():
        if request.method == 'POST' and 'photo' in request.files:
            lookup = photos.save(request.files['photo'])
            rec = Photo(lookup=lookup, user=g.user.id)
            rec.store()
            flash('Photo saved.')
            return redirect(url_for('show', id=rec.id))
        return render_template('upload.html')

    @app.route('/photo/<id>')
    def show(id):
        photo = Photo.load(id)
        if photo is None:
            abort(404)
        url = photos.get_url(photo.lookup)
        return render_template('show.html', url=url, photo=photo)

3. Конфигурация приложения
--------------------------

В ``Flask-Uploads`` для инициализации требуются все ранее созданные экземпляры :py:class:`~flask_uploads.UploadSet`:

.. code-block:: python

    from flask_uploads import configure_uploads

    configure_uploads(app, (photos,))

В ``Flask-Uploader`` достаточно вызвать функцию :py:func:`~flask_uploader.init_uploader`
с единственным обязательным аргументом - экземпляром приложения:

.. code-block:: python

    from flask_uploader import init_uploader

    init_uploader(app)

4. Предостережение
------------------

Рассмотренный выше код я бы не рекомендовал использовать в производственной среде.
Во-первых, в нем нет отлова исключений как для ``Flask-Uploads``, так и для ``Flask-Uploader``.
Во-вторых, ``Flask-Uploader`` дает больше возможностей по тонкой настройке и расширению.

Приведенный материал показывает ключевые моменты, связанные с переходом на мое расширение,
однако вам стоит прочитать всю документацию,
чтобы оценить весь масштаб возможностей и использовать расширение правильно.

.. _Flask-Uploads: https://github.com/maxcountryman/flask-uploads