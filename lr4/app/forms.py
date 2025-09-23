from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError, EqualTo
from app.models import User
import re

def validate_password(form, field):
    password = field.data
    if len(password) < 8 or len(password) > 128:
        raise ValidationError('Password must be 8-128 characters long')
    if not re.search(r'[A-ZА-Я]', password):
        raise ValidationError('Password must contain at least one uppercase letter')
    if not re.search(r'[a-zа-я]', password):
        raise ValidationError('Password must contain at least one lowercase letter')
    if not re.search(r'[0-9]', password):
        raise ValidationError('Password must contain at least one digit')
    if re.search(r'[^\w~!?@#$%^&*_\-+()\[\]{}><\/\\|"\'\.,:;]', password):
        raise ValidationError('Password contains invalid characters')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=5),
        Regexp(r'^[a-zA-Z0-9]+$', message='Username can only contain letters and numbers')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        validate_password
    ])
    last_name = StringField('Last Name')
    first_name = StringField('First Name', validators=[DataRequired()])
    middle_name = StringField('Middle Name')
    role_id = SelectField('Role', coerce=int)
    submit = SubmitField('Save')

class UserEditForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=50)])
    first_name = StringField('Имя', validators=[DataRequired(), Length(min=1, max=50)])
    last_name = StringField('Фамилия', validators=[DataRequired(), Length(min=1, max=50)])
    middle_name = StringField('Отчество', validators=[Length(max=50)])
    role_id = SelectField('Роль', coerce=int, validators=[DataRequired()])
    password = PasswordField('Новый пароль', validators=[Length(min=8, max=128)])
    confirm_password = PasswordField('Подтвердить пароль', validators=[EqualTo('password')])
    submit = SubmitField('Обновить')

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField('Подтвердить пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Текущий пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField('Подтвердить новый пароль', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Изменить пароль')