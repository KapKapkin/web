from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError, EqualTo
from app.models import User
import re

def validate_password_optional(form, field):
    password = field.data
    if password:
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
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class UserForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[
        DataRequired(),
        Length(min=5),
        Regexp(r'^[a-zA-Z0-9]+$', message='Имя пользователя может содержать только буквы и цифры')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(),
        validate_password
    ])
    confirm_password = PasswordField('Подтвердить пароль', validators=[
        DataRequired(),
        EqualTo('password', message='Пароли должны совпадать')
    ])
    last_name = StringField('Фамилия')
    first_name = StringField('Имя', validators=[DataRequired()])
    middle_name = StringField('Отчество')
    role_id = SelectField('Роль', coerce=int, validators=[DataRequired(message='Выберите роль')])
    submit = SubmitField('Сохранить')

class UserEditForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=50)])
    first_name = StringField('Имя', validators=[DataRequired(), Length(min=1, max=50)])
    last_name = StringField('Фамилия', validators=[DataRequired(), Length(min=1, max=50)])
    middle_name = StringField('Отчество', validators=[Length(max=50)])
    role_id = SelectField('Роль', coerce=int, validators=[DataRequired()])
    password = PasswordField('Новый пароль (оставьте пустым, чтобы не менять)', validators=[validate_password_optional])
    confirm_password = PasswordField('Подтвердить пароль', validators=[EqualTo('password', message='Пароли должны совпадать')])
    submit = SubmitField('Обновить')

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
