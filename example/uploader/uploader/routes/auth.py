from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
)
from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required,
)

from ..forms import LoginForm, ProfileForm
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
@login_required
def logout():
    logout_user()
    return redirect(request.referrer)


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user
    form = ProfileForm(obj=user)

    if form.validate_on_submit():
        form.populate_obj(user)
        user_manager.save(user)
        flash('Profile saved successfully.')
        return redirect(request.url)

    return render_template('profile.html', form=form)
