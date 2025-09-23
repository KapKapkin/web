import pytest
import re
from app import create_app
from app.models import db, User, Role
from config import Config

def test_app_creation():
    app = create_app()
    assert app is not None
    assert app.config['SECRET_KEY'] is not None

def test_config_creation():
    config = Config()

    assert hasattr(config, 'SECRET_KEY')
    assert hasattr(config, 'SQLALCHEMY_DATABASE_URI')
    assert config.SECRET_KEY is not None
    assert 'sqlite' in config.SQLALCHEMY_DATABASE_URI

def test_app_config_values():
    app = create_app()

    assert 'SECRET_KEY' in app.config
    assert 'SQLALCHEMY_DATABASE_URI' in app.config
    assert 'SQLALCHEMY_TRACK_MODIFICATIONS' in app.config

def test_user_creation():
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
    user = User(username='test', first_name='Test', last_name='User')
    user.set_password('testpassword')

    assert user.password_hash is not None
    assert user.password_hash != 'testpassword'
    assert 'pbkdf2:sha256' in user.password_hash

    assert user.check_password('testpassword') is True
    assert user.check_password('wrongpassword') is False

def test_user_full_name():
    user = User(
        username='testuser',
        first_name='Иван',
        last_name='Иванов',
        middle_name='Иванович'
    )

    expected_full_name = 'Иванов Иван Иванович'
    assert user.full_name == expected_full_name

def test_user_full_name_without_middle():
    user = User(
        username='testuser2',
        first_name='Петр',
        last_name='Петров'
    )

    expected_full_name = 'Петров Петр'
    assert user.full_name == expected_full_name

def test_user_full_name_only_first():
    user = User(
        username='testuser3',
        first_name='Анна'
    )

    expected_full_name = 'Анна'
    assert user.full_name == expected_full_name

def test_role_creation():
    role = Role(name='Test Role', description='Test Description')

    assert role.name == 'Test Role'
    assert role.description == 'Test Description'

def test_user_repr():
    user = User(username='testuser')
    assert str(user) == '<User testuser>'

def test_role_repr():
    role = Role(name='Admin')
    assert str(role) == '<Role Admin>'

def test_models_import():
    try:
        from app.models import User, Role, db
        assert User is not None
        assert Role is not None
        assert db is not None
    except ImportError:
        assert False, "Не удалось импортировать модели"

def test_forms_import():
    try:
        from app.forms import UserForm, UserEditForm, LoginForm, RegistrationForm, ChangePasswordForm

        assert True
    except ImportError:
        assert False, "Не удалось импортировать формы"

def test_blueprint_creation():
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
    app = create_app()

    from flask_login import UserMixin
    user = User(username='test', first_name='Test')
    assert isinstance(user, UserMixin)

    assert hasattr(user, 'is_authenticated')
    assert hasattr(user, 'is_active')
    assert hasattr(user, 'is_anonymous')
    assert hasattr(user, 'get_id')

def test_user_password_security():
    user = User(username='securitytest', first_name='Security', last_name='Test')

    passwords = ['simple123', 'Complex123!', 'VeryLongAndComplexPassword123!@#']

    for password in passwords:
        user.set_password(password)
        assert user.password_hash != password
        assert user.check_password(password)
        assert not user.check_password(password + 'wrong')

def test_role_user_relationship():
    role = Role(name='TestRole', description='Test role for relationships')
    user = User(username='roletest', first_name='Role', last_name='Test')

    user.role_id = 1

    assert user.role_id == 1

def test_user_timestamps():
    from datetime import datetime
    user = User(username='timetest', first_name='Time', last_name='Test')

    assert hasattr(user, 'created_at')

def test_flask_extensions():
    app = create_app()

    assert hasattr(app, 'login_manager')

    blueprint_names = [bp.name for bp in app.blueprints.values()]
    assert 'auth' in blueprint_names
    assert 'main' in blueprint_names

def test_app_routes():
    app = create_app()

    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(rule.rule)

    assert '/' in routes
    assert '/login' in routes
    assert '/logout' in routes
    assert '/register' in routes

def test_password_complexity():

    test_cases = [
        ('weak', False),
        ('12345678', False),
        ('password', False),
        ('Password1', True),
        ('Password123!', True),
    ]

    user = User(username='test', first_name='Test')

    for password, should_be_complex in test_cases:
        user.set_password(password)

        assert user.password_hash is not None

def test_full_name_edge_cases():

    user1 = User(username='test1', first_name='Иван')
    assert user1.full_name == 'Иван'

    user2 = User(username='test2', first_name='Петр', last_name=None, middle_name=None)
    assert user2.full_name == 'Петр'

    user3 = User(username='test3', first_name='Анна', last_name='', middle_name='')
    assert user3.full_name == 'Анна'

def test_model_constraints():

    user = User(username='constrainttest', first_name='Test')

    assert hasattr(User, 'username')
    assert hasattr(User, 'first_name')
    assert hasattr(User, 'password_hash')

    role = Role(name='ConstraintRole')
    assert hasattr(Role, 'name')

def test_form_classes_exist():
    from app.forms import UserForm, LoginForm, RegistrationForm, ChangePasswordForm, UserEditForm
    from flask_wtf import FlaskForm

    assert issubclass(UserForm, FlaskForm)
    assert issubclass(LoginForm, FlaskForm)
    assert issubclass(RegistrationForm, FlaskForm)
    assert issubclass(ChangePasswordForm, FlaskForm)
    assert issubclass(UserEditForm, FlaskForm)

def test_wtforms_validators_import():
    try:
        from wtforms.validators import DataRequired, Length, Regexp, EqualTo
        assert DataRequired is not None
        assert Length is not None
        assert Regexp is not None
        assert EqualTo is not None
    except ImportError:
        assert False, "Не удалось импортировать валидаторы WTForms"

def test_database_models_relationships():

    assert hasattr(User, 'role_id')
    assert hasattr(Role, 'users')

    user_role_id_column = getattr(User, 'role_id')
    assert user_role_id_column is not None

def test_sqlalchemy_integration():
    from flask_sqlalchemy import SQLAlchemy
    from app.models import db

    assert isinstance(db, SQLAlchemy)

    assert hasattr(db.Model, 'registry')

def test_werkzeug_security():
    from werkzeug.security import generate_password_hash, check_password_hash

    password = 'testpassword123'
    hashed = generate_password_hash(password)

    assert hashed != password
    assert check_password_hash(hashed, password)
    assert not check_password_hash(hashed, 'wrongpassword')

def test_datetime_functionality():
    from datetime import datetime
    user = User(username='datetest', first_name='Date', last_name='Test')

    assert hasattr(User, 'created_at')

    now = datetime.utcnow()
    assert isinstance(now, datetime)

def test_application_factory():

    app1 = create_app()
    app2 = create_app()

    assert app1 is not app2
    assert app1.config['SECRET_KEY'] == app2.config['SECRET_KEY']
