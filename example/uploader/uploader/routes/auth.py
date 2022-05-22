from flask import (
    Blueprint,
    flash,
    redirect,
    request,
)
from flask_login import (
    login_user,
    logout_user,
)

from ..extensions import mongo, User
from ..forms import LoginForm


bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.find(
            username=form.username.data,
            password=form.password.data,
        )

        if user is None:
            user_id = mongo.db.users.insert_one({
                'username': form.username.data,
                'password': form.password.data,
            }).inserted_id
            user = User(user_id, form.username.data)

        login_user(user)
    else:
        flash(form.errors)

    return redirect(request.referrer)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(request.referrer)
