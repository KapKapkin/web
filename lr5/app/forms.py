from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp
import re

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Обязательное поле'),
        Length(min=3, max=50, message='От 3 до 50 символов')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Обязательное поле')
    ])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Обязательное поле'),
        Length(min=3, max=50, message='От 3 до 50 символов'),
        Regexp(r'^[a-zA-Z0-9_]+$', message='Только латинские буквы, цифры и подчеркивания')
    ])

    first_name = StringField('Имя', validators=[
        DataRequired(message='Обязательное поле'),
        Length(min=1, max=50, message='От 1 до 50 символов')
    ])

    last_name = StringField('Фамилия', validators=[
        Length(max=50, message='Максимум 50 символов')
    ])

    middle_name = StringField('Отчество', validators=[
        Length(max=50, message='Максимум 50 символов')
    ])

    password = PasswordField('Пароль', validators=[
        DataRequired(message='Обязательное поле'),
        Length(min=8, message='Минимум 8 символов'),
        Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]',
            message='Пароль должен содержать: строчные и заглавные буквы, цифры, спецсимволы'
        )
    ])

    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired(message='Обязательное поле'),
        EqualTo('password', message='Пароли не совпадают')
    ])

    submit = SubmitField('Зарегистрироваться')

class UserForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Обязательное поле'),
        Length(min=3, max=50, message='От 3 до 50 символов'),
        Regexp(r'^[a-zA-Z0-9_]+$', message='Только латинские буквы, цифры и подчеркивания')
    ])

    first_name = StringField('Имя', validators=[
        DataRequired(message='Обязательное поле'),
        Length(min=1, max=50, message='От 1 до 50 символов')
    ])

    last_name = StringField('Фамилия', validators=[
        Length(max=50, message='Максимум 50 символов')
    ])

    middle_name = StringField('Отчество', validators=[
        Length(max=50, message='Максимум 50 символов')
    ])

    password = PasswordField('Пароль', validators=[
        DataRequired(message='Обязательное поле'),
        Length(min=8, message='Минимум 8 символов'),
        Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]',
            message='Пароль должен содержать: строчные и заглавные буквы, цифры, спецсимволы'
        )
    ])

    role_id = SelectField('Роль', coerce=int, validators=[
        DataRequired(message='Выберите роль')
    ])

    submit = SubmitField('Создать пользователя')

class UserEditForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Обязательное поле'),
        Length(min=3, max=50, message='От 3 до 50 символов'),
        Regexp(r'^[a-zA-Z0-9_]+$', message='Только латинские буквы, цифры и подчеркивания')
    ])

    first_name = StringField('Имя', validators=[
        DataRequired(message='Обязательное поле'),
        Length(min=1, max=50, message='От 1 до 50 символов')
    ])

    last_name = StringField('Фамилия', validators=[
        Length(max=50, message='Максимум 50 символов')
    ])

    middle_name = StringField('Отчество', validators=[
        Length(max=50, message='Максимум 50 символов')
    ])

    role_id = SelectField('Роль', coerce=int, validators=[
        DataRequired(message='Выберите роль')
    ])

    submit = SubmitField('Сохранить изменения')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Текущий пароль', validators=[
        DataRequired(message='Обязательное поле')
    ])

    new_password = PasswordField('Новый пароль', validators=[
        DataRequired(message='Обязательное поле'),
        Length(min=8, message='Минимум 8 символов'),
        Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]',
            message='Пароль должен содержать: строчные и заглавные буквы, цифры, спецсимволы'
        )
    ])

    confirm_password = PasswordField('Подтвердите новый пароль', validators=[
        DataRequired(message='Обязательное поле'),
        EqualTo('new_password', message='Пароли не совпадают')
    ])

    submit = SubmitField('Изменить пароль')
