.. _wtf:

Интеграция с WTForms
====================

Валидаторы
----------

Все :ref:`встроенные валидаторы <validators>`,
кроме :py:class:`~flask_uploader.validators.FileRequired` можно использовать с WTForms,
но импортировать их нужно из модуля ``flask_uploader.contrib.wtf``:

.. code-block:: python

    # Form description module, for example - forms.py

    from flask_wtf import FlaskForm
    from flask_wtf.file import FileField
    from flask_uploader.contrib.wtf import (
        Extension,
        FileSize,
        ImageSize,
    )
    from wtforms.validators import DataRequired


    class SongForm(FlaskForm):
        file = FileField(validators=[
            DataRequired(),
            Extension(
                {'mp3', 'flac'},
                message='This is not an audio file.',
            ),
            FileSize('50m'),
        ])
        cover = FileField(validators=[
            Extension(Extension.IMAGES),
            FileSize('2m'),
            ImageSize(
                min_width=250, min_height=250,
                message=ImageSize.SIZE_GREATER_EQUAL,
            ),
        ])

Модуль ``flask_wtf.file`` включает часто используемые валидаторы,
но я не рекомендую их использовать по объективным причинам.
Рассмотрим каждый валидатор в отдельности:

* :py:class:`~flask_wtf.file.FileRequired`

  Удобно использовать одну форму для добавления и редактирования сущности,
  однако из соображений безопасности браузер будет игнорировать значение поля
  :py:class:`~flask_wtf.file.FileField`.
  С добавлением проблем не будет, а вот при редактировании,
  если пользовать не выберет файл, будет ошибка.

  Вы можете использовать валидатор :py:class:`~wtforms.validators.DataRequired`,
  он прекрасно справляется с задачей редактирования.

* :py:class:`~flask_wtf.file.FileSize`

  Может упасть с исключением :py:class:`MemoryError` так как читывает все содержимое файла в оперативную память,
  чтобы определить его размер. Для больших файлов может повлиять на производительность.

  В моей реализации валидатор устанавливает внутренний курсор в конец файла,
  считывает значение и возвращает его обратно в начало,
  это работает на файлах любого размера мгновенно.
  Второй плюс моей реализации - человекопонятные единицы измерения.

* :py:class:`~flask_wtf.file.FileAllowed`

  Можно использовать этот валидатор, если он вам привычнее, либо мой :py:class:`~flask_uploader.contrib.wtf.Extension`.

Новый валидатор
~~~~~~~~~~~~~~~

:ref:`Ранее <validators:Новый валидатор>` я приводил пример пользовательского валидатора.
Его необходимо задекорировать декоратором :py:func:`~flask_uploader.contrib.wtf.wrap_validator`,
чтобы он работал с ``WTForms``:

.. code-block:: python

    from flask_wtf import FlaskForm
    from flask_wtf.file import FileField
    from flask_uploader.contrib.wtf import Extension, wrap_validator


    IsJSON = is_json = wrap_validator(IsJSON)


    class PackageForm(FlaskForm):
        file = FileField(validators=[
            Extension({'json'}),
            IsJSON(),
        ])


Поле загрузчика
---------------

``Flask-Uploader`` реализует элемент формы :py:class:`~flask_uploader.contrib.wtf.UploadField`.
Конструктор принимает обязательный именованный аргумент ``uploader``
- экземпляр :ref:`загрузчика <index:Создание загрузчика>`,
который используется для сохранения файла и установки значения атрибута модели.

Рассмотрим пример с формой редактирования профиля пользователя:

.. code-block:: python

    from flask_wtf import FlaskForm
    from flask_uploader import Uploader
    from flask_uploader.contrib.wtf import (
        Extension,
        UploadField,
    )
    from flask_uploader.storages import FileSystemStorage
    from wtforms.fields import StringField
    from wtforms.validators import Length


    class ProfileForm(FlaskForm):
        firstname = StringField(validators=[Length(min=1)])
        lastname = StringField(validators=[Length(min=1)])
        avatar = UploadField(
            uploader=Uploader(
                'avatars', FileSystemStorage(dest='avatars')
            ),
            overwrite=True,
            validators=[
                Extension(Extension.IMAGES),
            ]
        )

Мы создали загрузчик с именем ``avatars``, который будет сохранять загруженную пользователем
аватарку в файловой системе. После сохранения файла, атрибуту ``avatar``
будет присвоен поисковый идентификатор, который можно использовать в аргументе методов
:py:meth:`~flask_uploader.core.Uploader.load` или :py:meth:`~flask_uploader.core.Uploader.remove`:

.. code-block:: python

    form = ProfileForm()

    if form.validate_on_submit():
        print(type(form.avatar.data).__name__)  # FileStorage
        form.avatar.save()
        print(type(form.avatar.data).__name__)  # str

Вызывать метод :py:meth:`~flask_uploader.contrib.wtf.UploadField.save` вручную не обязательно,
в большинстве случаев вы используете метод :py:meth:`~wtforms.form.BaseForm.populate_obj`
для присвоения значений полей формы атрибутам модели,
в этот момент для всех полей :py:class:`~flask_uploader.contrib.wtf.UploadField`
будет вызван метод :py:meth:`~flask_uploader.contrib.wtf.UploadField.save`:

.. code-block:: python

    from flask import Blueprint
    from flask_login import current_user, login_required


    bp = Blueprint('auth', __name__)


    @bp.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        user = current_user
        form = ProfileForm(obj=user)

        if form.validate_on_submit():
            form.populate_obj(user)
            # Saving a user
            return redirect(request.url)

        return render_template('profile.html', form=form)

Конструктору :py:class:`~flask_uploader.contrib.wtf.UploadField` можно передать и другие именованные аргументы:

* ``overwrite`` - перезаписать существующий файл, по-умолчанию :py:data:`False`;
* ``return_url`` - после сохранения присвоить URL-адрес файла, по-умолчанию :py:data:`False`;
* ``external`` - создать абсолютный URL, по-умолчанию :py:data:`False`.
