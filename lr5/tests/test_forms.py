import pytest
import tempfile
import os
from app import create_app, db
from app.models import User, Role
from app.forms import LoginForm, RegistrationForm, UserEditForm, ChangePasswordForm
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Создаёт тестовое приложение"""
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False
    })
    
    with app.app_context():
        db.create_all()
        # Создаём роли
        admin_role = Role(name='admin')
        user_role = Role(name='user')
        db.session.add(admin_role)
        db.session.add(user_role)
        
        # Создаём тестового пользователя
        test_user = User(
            login='testuser',
            first_name='Test',
            last_name='User',
            email='test@test.com',
            password_hash=generate_password_hash('Password123!'),
            role=user_role
        )
        db.session.add(test_user)
        db.session.commit()
    
    yield app
    
    os.close(db_fd)
    os.unlink(db_path)


class TestLoginForm:
    """Тесты формы входа"""
    
    def test_basic_validation(self, app):
        """Тест базовой валидации формы входа"""
        with app.app_context():
            form = LoginForm(data={
                'username': 'testuser',
                'password': 'password123'
            })
            # Проверяем, что данные присутствуют
            assert form.username.data == 'testuser'
            assert form.password.data == 'password123'
    
    def test_empty_login_form(self, app):
        """Тест пустой формы входа"""
        with app.app_context():
            form = LoginForm(data={
                'username': '',
                'password': ''
            })
            assert form.validate() is False


class TestRegistrationForm:
    """Тесты формы регистрации"""
    
    def test_basic_validation(self, app):
        """Тест базовой валидации формы регистрации"""
        with app.app_context():
            form = RegistrationForm(data={
                'username': 'newuser',
                'first_name': 'New',
                'last_name': 'User',
                'password': 'Password123!',
                'confirm_password': 'Password123!'
            })
            # Проверяем данные
            assert form.username.data == 'newuser'
            assert form.first_name.data == 'New'
    
    def test_password_mismatch(self, app):
        """Тест несовпадения паролей"""
        with app.app_context():
            form = RegistrationForm(data={
                'username': 'newuser',
                'first_name': 'New',
                'last_name': 'User',
                'password': 'Password123!',
                'confirm_password': 'DifferentPass123!'
            })
            assert form.validate() is False


class TestUserEditForm:
    """Тесты формы редактирования пользователя"""
    
    def test_basic_validation(self, app):
        """Тест базовой валидации формы редактирования"""
        with app.app_context():
            role = Role.query.filter_by(name='user').first()
            
            form = UserEditForm(data={
                'username': 'editeduser',
                'first_name': 'Edited',
                'last_name': 'Name',
                'role_id': role.id
            })
            
            assert form.username.data == 'editeduser'
            assert form.first_name.data == 'Edited'


class TestChangePasswordForm:
    """Тесты формы смены пароля"""
    
    def test_basic_validation(self, app):
        """Тест базовой валидации формы смены пароля"""
        with app.app_context():
            form = ChangePasswordForm(data={
                'old_password': 'Password123!',
                'new_password': 'NewPassword123!',
                'confirm_password': 'NewPassword123!'
            })
            
            assert form.old_password.data == 'Password123!'
            assert form.new_password.data == 'NewPassword123!'


if __name__ == '__main__':
    pytest.main([__file__])


class TestLoginForm:
    """Тесты формы входа"""
    
    def test_valid_login_form(self, app):
        """Тест валидной формы входа"""
        with app.app_context():
            form = LoginForm(data={
                'login': 'testuser',
                'password': 'test123'
            })
            assert form.validate() is True
    
    def test_empty_login_form(self, app):
        """Тест пустой формы входа"""
        with app.app_context():
            form = LoginForm(data={
                'login': '',
                'password': ''
            })
            assert form.validate() is False
            assert 'Обязательное поле.' in form.login.errors
            assert 'Обязательное поле.' in form.password.errors
    
    def test_invalid_credentials(self, app):
        """Тест неправильных учётных данных"""
        with app.app_context():
            form = LoginForm(data={
                'login': 'nonexistent',
                'password': 'wrongpassword'
            })
            assert form.validate() is False
            assert 'Неправильный логин или пароль' in form.login.errors
    
    def test_correct_user_wrong_password(self, app):
        """Тест правильного пользователя с неправильным паролем"""
        with app.app_context():
            form = LoginForm(data={
                'login': 'testuser',
                'password': 'wrongpassword'
            })
            assert form.validate() is False
            assert 'Неправильный логин или пароль' in form.login.errors


class TestRegistrationForm:
    """Тесты формы регистрации"""
    
    def test_valid_registration_form(self, app):
        """Тест валидной формы регистрации"""
        with app.app_context():
            form = RegistrationForm(data={
                'login': 'newuser',
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@test.com',
                'password': 'newpass123',
                'password2': 'newpass123'
            })
            assert form.validate() is True
    
    def test_empty_registration_form(self, app):
        """Тест пустой формы регистрации"""
        with app.app_context():
            form = RegistrationForm()
            assert form.validate() is False
            assert 'Обязательное поле.' in form.login.errors
            assert 'Обязательное поле.' in form.first_name.errors
            assert 'Обязательное поле.' in form.last_name.errors
            assert 'Обязательное поле.' in form.email.errors
            assert 'Обязательное поле.' in form.password.errors
    
    def test_duplicate_login(self, app):
        """Тест дублирующегося логина"""
        with app.app_context():
            form = RegistrationForm(data={
                'login': 'testuser',  # Уже существует
                'first_name': 'Another',
                'last_name': 'User',
                'email': 'another@test.com',
                'password': 'password123',
                'password2': 'password123'
            })
            assert form.validate() is False
            assert 'Пользователь с таким логином уже существует' in form.login.errors
    
    def test_duplicate_email(self, app):
        """Тест дублирующегося email"""
        with app.app_context():
            form = RegistrationForm(data={
                'login': 'newuser',
                'first_name': 'New',
                'last_name': 'User',
                'email': 'test@test.com',  # Уже существует
                'password': 'password123',
                'password2': 'password123'
            })
            assert form.validate() is False
            assert 'Пользователь с таким email уже существует' in form.email.errors
    
    def test_password_mismatch(self, app):
        """Тест несовпадения паролей"""
        with app.app_context():
            form = RegistrationForm(data={
                'login': 'newuser',
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@test.com',
                'password': 'password123',
                'password2': 'differentpassword'
            })
            assert form.validate() is False
            assert 'Пароли должны совпадать' in form.password2.errors
    
    def test_invalid_email_format(self, app):
        """Тест неправильного формата email"""
        with app.app_context():
            form = RegistrationForm(data={
                'login': 'newuser',
                'first_name': 'New',
                'last_name': 'User',
                'email': 'invalid-email',
                'password': 'password123',
                'password2': 'password123'
            })
            assert form.validate() is False
            assert 'Неверный адрес электронной почты.' in form.email.errors
    
    def test_short_password(self, app):
        """Тест слишком короткого пароля"""
        with app.app_context():
            form = RegistrationForm(data={
                'login': 'newuser',
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@test.com',
                'password': '123',  # Слишком короткий
                'password2': '123'
            })
            assert form.validate() is False
            assert 'Размер поля должен быть не менее 6 символов.' in form.password.errors


class TestUserEditForm:
    """Тесты формы редактирования пользователя"""
    
    def test_valid_edit_form(self, app):
        """Тест валидной формы редактирования"""
        with app.app_context():
            user = User.query.filter_by(login='testuser').first()
            role = Role.query.filter_by(name='user').first()
            
            form = EditUserForm(data={
                'login': 'testuser',
                'first_name': 'Updated',
                'last_name': 'Name',
                'email': 'updated@test.com',
                'role_id': role.id
            })
            form.original_user = user
            assert form.validate() is True
    
    def test_edit_form_with_same_data(self, app):
        """Тест формы редактирования с теми же данными"""
        with app.app_context():
            user = User.query.filter_by(login='testuser').first()
            
            form = EditUserForm(data={
                'login': user.login,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role_id': user.role_id
            })
            form.original_user = user
            assert form.validate() is True
    
    def test_edit_form_duplicate_login(self, app):
        """Тест изменения логина на уже существующий"""
        with app.app_context():
            # Создаём ещё одного пользователя
            user_role = Role.query.filter_by(name='user').first()
            another_user = User(
                login='another',
                first_name='Another',
                last_name='User',
                email='another@test.com',
                password_hash=generate_password_hash('pass123'),
                role=user_role
            )
            db.session.add(another_user)
            db.session.commit()
            
            # Пытаемся изменить логин на уже существующий
            user = User.query.filter_by(login='testuser').first()
            form = EditUserForm(data={
                'login': 'another',  # Уже существует
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test@test.com',
                'role_id': user.role_id
            })
            form.original_user = user
            assert form.validate() is False
            assert 'Пользователь с таким логином уже существует' in form.login.errors
    
    def test_edit_form_duplicate_email(self, app):
        """Тест изменения email на уже существующий"""
        with app.app_context():
            # Создаём ещё одного пользователя
            user_role = Role.query.filter_by(name='user').first()
            another_user = User(
                login='another',
                first_name='Another',
                last_name='User',
                email='another@test.com',
                password_hash=generate_password_hash('pass123'),
                role=user_role
            )
            db.session.add(another_user)
            db.session.commit()
            
            # Пытаемся изменить email на уже существующий
            user = User.query.filter_by(login='testuser').first()
            form = EditUserForm(data={
                'login': 'testuser',
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'another@test.com',  # Уже существует
                'role_id': user.role_id
            })
            form.original_user = user
            assert form.validate() is False
            assert 'Пользователь с таким email уже существует' in form.email.errors
    
    def test_edit_form_empty_fields(self, app):
        """Тест формы редактирования с пустыми полями"""
        with app.app_context():
            user = User.query.filter_by(login='testuser').first()
            form = EditUserForm(data={
                'login': '',
                'first_name': '',
                'last_name': '',
                'email': '',
                'role_id': ''
            })
            form.original_user = user
            assert form.validate() is False
            assert 'Обязательное поле.' in form.login.errors
            assert 'Обязательное поле.' in form.first_name.errors
            assert 'Обязательное поле.' in form.last_name.errors
            assert 'Обязательное поле.' in form.email.errors


class TestChangePasswordForm:
    """Тесты формы смены пароля"""
    
    def test_valid_change_password_form(self, app):
        """Тест валидной формы смены пароля"""
        with app.app_context():
            form = ChangePasswordForm(data={
                'old_password': 'test123',
                'new_password': 'newpass123',
                'confirm_password': 'newpass123'
            })
            
            # Устанавливаем текущего пользователя для валидации
            user = User.query.filter_by(login='testuser').first()
            form.current_user = user
            
            assert form.validate() is True
    
    def test_wrong_old_password(self, app):
        """Тест неправильного старого пароля"""
        with app.app_context():
            form = ChangePasswordForm(data={
                'old_password': 'wrongpassword',
                'new_password': 'newpass123',
                'confirm_password': 'newpass123'
            })
            
            user = User.query.filter_by(login='testuser').first()
            form.current_user = user
            
            assert form.validate() is False
            assert 'Неправильный текущий пароль' in form.old_password.errors
    
    def test_new_password_mismatch(self, app):
        """Тест несовпадения новых паролей"""
        with app.app_context():
            form = ChangePasswordForm(data={
                'old_password': 'test123',
                'new_password': 'newpass123',
                'confirm_password': 'differentpass'
            })
            
            user = User.query.filter_by(login='testuser').first()
            form.current_user = user
            
            assert form.validate() is False
            assert 'Пароли должны совпадать' in form.confirm_password.errors
    
    def test_short_new_password(self, app):
        """Тест слишком короткого нового пароля"""
        with app.app_context():
            form = ChangePasswordForm(data={
                'old_password': 'test123',
                'new_password': '123',  # Слишком короткий
                'confirm_password': '123'
            })
            
            user = User.query.filter_by(login='testuser').first()
            form.current_user = user
            
            assert form.validate() is False
            assert 'Размер поля должен быть не менее 6 символов.' in form.new_password.errors
    
    def test_empty_change_password_form(self, app):
        """Тест пустой формы смены пароля"""
        with app.app_context():
            form = ChangePasswordForm()
            user = User.query.filter_by(login='testuser').first()
            form.current_user = user
            
            assert form.validate() is False
            assert 'Обязательное поле.' in form.old_password.errors
            assert 'Обязательное поле.' in form.new_password.errors
            assert 'Обязательное поле.' in form.confirm_password.errors


class TestFormFieldValidation:
    """Тесты валидации отдельных полей форм"""
    
    def test_login_field_length(self, app):
        """Тест длины поля логина"""
        with app.app_context():
            # Слишком короткий логин
            form = RegistrationForm(data={
                'login': 'a',  # 1 символ
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test@example.com',
                'password': 'password123',
                'password2': 'password123'
            })
            assert form.validate() is False
            assert 'Размер поля должен быть от 3 до 20 символов.' in form.login.errors
            
            # Слишком длинный логин
            form = RegistrationForm(data={
                'login': 'a' * 25,  # 25 символов
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test@example.com',
                'password': 'password123',
                'password2': 'password123'
            })
            assert form.validate() is False
            assert 'Размер поля должен быть от 3 до 20 символов.' in form.login.errors
    
    def test_name_fields_length(self, app):
        """Тест длины полей имени и фамилии"""
        with app.app_context():
            # Слишком длинное имя
            form = RegistrationForm(data={
                'login': 'testuser',
                'first_name': 'A' * 35,  # 35 символов
                'last_name': 'User',
                'email': 'test@example.com',
                'password': 'password123',
                'password2': 'password123'
            })
            assert form.validate() is False
            assert 'Размер поля должен быть не более 30 символов.' in form.first_name.errors
            
            # Слишком длинная фамилия
            form = RegistrationForm(data={
                'login': 'testuser',
                'first_name': 'Test',
                'last_name': 'U' * 35,  # 35 символов
                'email': 'test@example.com',
                'password': 'password123',
                'password2': 'password123'
            })
            assert form.validate() is False
            assert 'Размер поля должен быть не более 30 символов.' in form.last_name.errors
    
    def test_email_field_length(self, app):
        """Тест длины поля email"""
        with app.app_context():
            # Слишком длинный email
            long_email = 'a' * 100 + '@example.com'  # Больше 120 символов
            form = RegistrationForm(data={
                'login': 'testuser',
                'first_name': 'Test',
                'last_name': 'User',
                'email': long_email,
                'password': 'password123',
                'password2': 'password123'
            })
            assert form.validate() is False
            assert 'Размер поля должен быть не более 120 символов.' in form.email.errors


if __name__ == '__main__':
    pytest.main([__file__])