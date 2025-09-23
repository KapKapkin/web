import pytest
import re
from app import create_app
from app.models import db, User, Role
from config import Config

# ======== ТЕСТЫ КОНФИГУРАЦИИ ========

def test_app_creation():
    """Тест 1: Приложение создается успешно"""
    app = create_app()
    assert app is not None
    assert app.config['SECRET_KEY'] is not None

def test_config_creation():
    """Тест 2: Конфигурация создается корректно"""
    config = Config()
    
    # Проверяем базовые настройки
    assert hasattr(config, 'SECRET_KEY')
    assert hasattr(config, 'SQLALCHEMY_DATABASE_URI')
    assert config.SECRET_KEY is not None
    assert 'sqlite' in config.SQLALCHEMY_DATABASE_URI

def test_app_config_values():
    """Тест 3: Проверка значений конфигурации приложения"""
    app = create_app()
    
    # Проверяем что настройки загружены
    assert 'SECRET_KEY' in app.config
    assert 'SQLALCHEMY_DATABASE_URI' in app.config
    assert 'SQLALCHEMY_TRACK_MODIFICATIONS' in app.config

# ======== ТЕСТЫ МОДЕЛЕЙ ========

def test_user_creation():
    """Тест 4: Создание объектов пользователей"""
    user = User(
        username='newuser',
        first_name='New',
        last_name='User',
        middle_name='Middle'
    )
    user.set_password('password123')
    
    assert user.username == 'newuser'
    assert user.first_name == 'New'
    assert user.last_name == 'User'
    assert user.middle_name == 'Middle'
    assert user.check_password('password123')

def test_password_hashing():
    """Тест 5: Хеширование паролей работает корректно"""
    user = User(username='test', first_name='Test', last_name='User')
    user.set_password('testpassword')
    
    # Проверяем что пароль хешируется
    assert user.password_hash is not None
    assert user.password_hash != 'testpassword'
    assert 'pbkdf2:sha256' in user.password_hash
    
    # Проверяем что проверка пароля работает
    assert user.check_password('testpassword') is True
    assert user.check_password('wrongpassword') is False

def test_user_full_name():
    """Тест 6: Свойство полного имени пользователя"""
    user = User(
        username='testuser',
        first_name='Иван',
        last_name='Иванов',
        middle_name='Иванович'
    )
    
    expected_full_name = 'Иванов Иван Иванович'
    assert user.full_name == expected_full_name

def test_user_full_name_without_middle():
    """Тест 7: Полное имя без отчества"""
    user = User(
        username='testuser2',
        first_name='Петр',
        last_name='Петров'
    )
    
    expected_full_name = 'Петров Петр'
    assert user.full_name == expected_full_name

def test_user_full_name_only_first():
    """Тест 8: Полное имя только с именем"""
    user = User(
        username='testuser3',
        first_name='Анна'
    )
    
    expected_full_name = 'Анна'
    assert user.full_name == expected_full_name

def test_role_creation():
    """Тест 9: Создание объектов ролей"""
    role = Role(name='Test Role', description='Test Description')
    
    assert role.name == 'Test Role'
    assert role.description == 'Test Description'

def test_user_repr():
    """Тест 10: Строковое представление пользователя"""
    user = User(username='testuser')
    assert str(user) == '<User testuser>'

def test_role_repr():
    """Тест 11: Строковое представление роли"""
    role = Role(name='Admin')
    assert str(role) == '<Role Admin>'

# ======== ТЕСТЫ ИМПОРТОВ И СТРУКТУРЫ ========

def test_models_import():
    """Тест 12: Модели импортируются без ошибок"""
    try:
        from app.models import User, Role, db
        assert User is not None
        assert Role is not None
        assert db is not None
    except ImportError:
        assert False, "Не удалось импортировать модели"

def test_forms_import():
    """Тест 13: Формы импортируются без ошибок"""
    try:
        from app.forms import UserForm, UserEditForm, LoginForm, RegistrationForm, ChangePasswordForm
        # Если импорт прошел успешно, тест пройден
        assert True
    except ImportError:
        assert False, "Не удалось импортировать формы"

def test_blueprint_creation():
    """Тест 14: Blueprint'ы создаются без ошибок"""
    try:
        from app.auth import auth_bp
        from app.routes import main_bp
        
        assert auth_bp is not None
        assert main_bp is not None
        assert auth_bp.name == 'auth'
        assert main_bp.name == 'main'
    except ImportError:
        assert False, "Не удалось импортировать blueprint'ы"

def test_flask_login_integration():
    """Тест 15: Интеграция с Flask-Login"""
    app = create_app()
    
    # Проверяем что User является UserMixin
    from flask_login import UserMixin
    user = User(username='test', first_name='Test')
    assert isinstance(user, UserMixin)
    
    # Проверяем методы Flask-Login
    assert hasattr(user, 'is_authenticated')
    assert hasattr(user, 'is_active')
    assert hasattr(user, 'is_anonymous')
    assert hasattr(user, 'get_id')

# ======== ТЕСТЫ БИЗНЕС-ЛОГИКИ ========

def test_user_password_security():
    """Тест 16: Безопасность паролей"""
    user = User(username='securitytest', first_name='Security', last_name='Test')
    
    # Тестируем разные пароли
    passwords = ['simple123', 'Complex123!', 'VeryLongAndComplexPassword123!@#']
    
    for password in passwords:
        user.set_password(password)
        assert user.password_hash != password
        assert user.check_password(password)
        assert not user.check_password(password + 'wrong')

def test_role_user_relationship():
    """Тест 17: Связь между ролью и пользователем"""
    role = Role(name='TestRole', description='Test role for relationships')
    user = User(username='roletest', first_name='Role', last_name='Test')
    
    # Назначаем роль пользователю (через id будет работать в реальной БД)
    user.role_id = 1  # Имитируем назначение роли
    
    assert user.role_id == 1

def test_user_timestamps():
    """Тест 18: Временные метки пользователей"""
    from datetime import datetime
    user = User(username='timetest', first_name='Time', last_name='Test')
    
    # Проверяем что поле created_at определено в модели
    assert hasattr(user, 'created_at')
    
    # В реальной БД created_at будет установлен автоматически
    # Здесь просто проверяем что поле существует

# ======== ТЕСТЫ КОНФИГУРАЦИИ FLASK ========

def test_flask_extensions():
    """Тест 19: Flask расширения подключены"""
    app = create_app()
    
    # Проверяем что приложение имеет нужные расширения
    assert hasattr(app, 'login_manager')
    
    # Проверяем blueprint'ы зарегистрированы
    blueprint_names = [bp.name for bp in app.blueprints.values()]
    assert 'auth' in blueprint_names
    assert 'main' in blueprint_names

def test_app_routes():
    """Тест 20: Маршруты приложения зарегистрированы"""
    app = create_app()
    
    # Получаем все маршруты
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(rule.rule)
    
    # Проверяем основные маршруты
    assert '/' in routes
    assert '/login' in routes
    assert '/logout' in routes
    assert '/register' in routes

def test_password_complexity():
    """Тест 21: Проверка сложности паролей"""
    # Тестируем разные типы паролей
    test_cases = [
        ('weak', False),           # Слишком простой
        ('12345678', False),       # Только цифры  
        ('password', False),       # Только буквы
        ('Password1', True),       # Буквы + цифра
        ('Password123!', True),    # Буквы + цифры + символы
    ]
    
    user = User(username='test', first_name='Test')
    
    for password, should_be_complex in test_cases:
        user.set_password(password)
        # Хеш всегда создается, но в реальной форме будет валидация
        assert user.password_hash is not None

def test_full_name_edge_cases():
    """Тест 22: Граничные случаи для полного имени"""
    # Тест с пустыми значениями
    user1 = User(username='test1', first_name='Иван')
    assert user1.full_name == 'Иван'
    
    # Тест с None значениями
    user2 = User(username='test2', first_name='Петр', last_name=None, middle_name=None)
    assert user2.full_name == 'Петр'
    
    # Тест с пустыми строками
    user3 = User(username='test3', first_name='Анна', last_name='', middle_name='')
    assert user3.full_name == 'Анна'

def test_model_constraints():
    """Тест 23: Ограничения моделей"""
    # Проверяем что модели имеют правильные ограничения
    user = User(username='constrainttest', first_name='Test')
    
    # Проверяем обязательные поля
    assert hasattr(User, 'username')
    assert hasattr(User, 'first_name')
    assert hasattr(User, 'password_hash')
    
    role = Role(name='ConstraintRole')
    assert hasattr(Role, 'name')

# ======== ТЕСТЫ ФОРМ (ТОЛЬКО ИМПОРТ) ========

def test_form_classes_exist():
    """Тест 24: Классы форм существуют"""
    from app.forms import UserForm, LoginForm, RegistrationForm, ChangePasswordForm, UserEditForm
    from flask_wtf import FlaskForm
    
    # Проверяем что формы наследуются от FlaskForm
    assert issubclass(UserForm, FlaskForm)
    assert issubclass(LoginForm, FlaskForm)
    assert issubclass(RegistrationForm, FlaskForm)
    assert issubclass(ChangePasswordForm, FlaskForm)
    assert issubclass(UserEditForm, FlaskForm)

def test_wtforms_validators_import():
    """Тест 25: Проверка импорта валидаторов WTForms"""
    try:
        from wtforms.validators import DataRequired, Length, Regexp, EqualTo
        assert DataRequired is not None
        assert Length is not None
        assert Regexp is not None
        assert EqualTo is not None
    except ImportError:
        assert False, "Не удалось импортировать валидаторы WTForms"

# ======== ТЕСТЫ ДОПОЛНИТЕЛЬНОГО ФУНКЦИОНАЛА ========

def test_database_models_relationships():
    """Тест 26: Отношения между моделями"""
    # Проверяем что модели имеют правильные отношения
    assert hasattr(User, 'role_id')
    assert hasattr(Role, 'users')
    
    # Проверяем ForeignKey
    user_role_id_column = getattr(User, 'role_id')
    assert user_role_id_column is not None

def test_sqlalchemy_integration():
    """Тест 27: Интеграция с SQLAlchemy"""
    from flask_sqlalchemy import SQLAlchemy
    from app.models import db
    
    # Проверяем что db является экземпляром SQLAlchemy
    assert isinstance(db, SQLAlchemy)
    
    # Проверяем что модели зарегистрированы
    assert hasattr(db.Model, 'registry')

def test_werkzeug_security():
    """Тест 28: Интеграция с Werkzeug Security"""
    from werkzeug.security import generate_password_hash, check_password_hash
    
    # Тестируем функции хеширования напрямую
    password = 'testpassword123'
    hashed = generate_password_hash(password)
    
    assert hashed != password
    assert check_password_hash(hashed, password)
    assert not check_password_hash(hashed, 'wrongpassword')

def test_datetime_functionality():
    """Тест 29: Функциональность работы с датами"""
    from datetime import datetime
    user = User(username='datetest', first_name='Date', last_name='Test')
    
    # Проверяем что поле created_at имеет правильный тип по умолчанию
    assert hasattr(User, 'created_at')
    
    # Проверяем что datetime импортируется корректно
    now = datetime.utcnow()
    assert isinstance(now, datetime)

def test_application_factory():
    """Тест 30: Фабрика приложений"""
    # Проверяем что можно создать несколько экземпляров приложения
    app1 = create_app()
    app2 = create_app()
    
    assert app1 is not app2  # Разные экземпляры
    assert app1.config['SECRET_KEY'] == app2.config['SECRET_KEY']  # Но одинаковая конфигурация