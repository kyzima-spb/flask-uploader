from __future__ import annotations
import typing as t

from flask_wtf.file import FileField
from werkzeug.datastructures import FileStorage
from wtforms.form import Form


FilenameStrategyCallable = t.Callable[[FileStorage], str]
ValidatorCallable = t.Callable[[FileStorage], None]
WTFValidatorCallable = t.Callable[[Form, FileField], None]
