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

from ..forms import LoginForm
from ..models import User, Manager


bp = Blueprint('auth', __name__)
user_manager = Manager(User)


@bp.route('/login', methods=['POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = user_manager.find_one(
            username=form.username.data,
            password=form.password.data,
        )

        if user is None:
            user = User()
            form.populate_obj(user)
            user_manager.save(user)

        login_user(user)
    else:
        flash(form.errors)

    return redirect(request.referrer)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(request.referrer)
