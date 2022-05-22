from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField
from wtforms.validators import InputRequired, Length


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=1)])
    password = PasswordField(validators=[InputRequired(), Length(min=1)])
