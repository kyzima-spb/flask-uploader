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

