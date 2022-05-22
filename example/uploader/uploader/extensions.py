from __future__ import annotations
import typing as t

from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask_login import LoginManager, UserMixin
from flask_pymongo import PyMongo
from flask_wtf import CSRFProtect
from flask_uploader.contrib.aws import AWS


csrf = CSRFProtect()
mongo = PyMongo()
aws = AWS()

login_manager = LoginManager()
login_manager.login_view = 'site.photos.index'


class User(UserMixin):
    def __init__(self, user_id: ObjectId, username: str) -> None:
        self.id = user_id
        self.username = username

    @classmethod
    def find(cls, **criteria) -> t.Optional[User]:
        user = mongo.db.users.find_one(criteria)

        if user is not None:
            user = cls(user['_id'], user['username'])

        return user

    @classmethod
    def get(cls, user_id: str) -> t.Optional[User]:
        try:
            return cls.find(_id=ObjectId(user_id))
        except InvalidId:
            return None


@login_manager.user_loader
def load_user(user_id: str) -> t.Optional[User]:
    return User.get(user_id)
