from __future__ import annotations
import typing as t

from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_uploader.contrib.aws import AWS

from .models import User, Manager


csrf = CSRFProtect()
aws = AWS()

login_manager = LoginManager()
login_manager.login_view = 'site.photos.index'


@login_manager.user_loader
def load_user(user_id: str) -> t.Optional[User]:
    user_manager = Manager[User](User)
    return user_manager.get(user_id)
