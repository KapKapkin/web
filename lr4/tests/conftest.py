import pytest
import os
import tempfile
from app import create_app, db
from app.models import User, Role

@pytest.fixture
def app():

    db_fd, db_path = tempfile.mkstemp()

    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def roles(app):
    with app.app_context():
        admin_role = Role(name='Администратор', description='Полный доступ')
        user_role = Role(name='Пользователь', description='Обычный пользователь')

        db.session.add(admin_role)
        db.session.add(user_role)
        db.session.commit()

        return {'admin': admin_role, 'user': user_role}

@pytest.fixture
def admin_user(app, roles):
    with app.app_context():
        user = User(
            username='admin',
            first_name='Админ',
            last_name='Тестовый',
            role_id=roles['admin'].id
        )
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def regular_user(app, roles):
    with app.app_context():
        user = User(
            username='user',
            first_name='Юзер',
            last_name='Тестовый',
            role_id=roles['user'].id
        )
        user.set_password('user123')
        db.session.add(user)
        db.session.commit()
        return user

def login_user(client, username, password):
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)

def logout_user(client):
    return client.get('/logout', follow_redirects=True)
