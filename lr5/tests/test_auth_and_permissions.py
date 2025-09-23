import pytest
import tempfile
import os
from app import create_app, db
from app.models import User, Role, VisitLog
from werkzeug.security import generate_password_hash
import io
import csv

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
        SECRET_KEY = 'test-secret-key'
        WTF_CSRF_ENABLED = False

    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        admin_role = Role(name='admin')
        user_role = Role(name='user')
        db.session.add(admin_role)
        db.session.add(user_role)

        admin_user = User(
            login='admin',
            first_name='Admin',
            last_name='User',
            email='admin@test.com',
            password_hash=generate_password_hash('admin123'),
            role=admin_role
        )

        test_user = User(
            login='testuser',
            first_name='Test',
            last_name='User',
            email='test@test.com',
            password_hash=generate_password_hash('test123'),
            role=user_role
        )

        another_user = User(
            login='another',
            first_name='Another',
            last_name='User',
            email='another@test.com',
            password_hash=generate_password_hash('another123'),
            role=user_role
        )

        db.session.add(admin_user)
        db.session.add(test_user)
        db.session.add(another_user)
        db.session.commit()

    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def login_user(client, login, password):
    return client.post('/auth/login', data={
        'login': login,
        'password': password
    }, follow_redirects=True)

def logout_user(client):
    return client.get('/auth/logout', follow_redirects=True)

class TestAuth:

    def test_login_page(self, client):
        rv = client.get('/auth/login')
        assert rv.status_code == 200
        assert 'Вход в систему' in rv.get_data(as_text=True)

    def test_register_page(self, client):
        rv = client.get('/auth/register')
        assert rv.status_code == 200
        assert 'Регистрация' in rv.get_data(as_text=True)

    def test_successful_login(self, client):
        rv = login_user(client, 'admin', 'admin123')
        assert rv.status_code == 200
        assert 'admin' in rv.get_data(as_text=True)

    def test_invalid_login(self, client):
        rv = client.post('/auth/login', data={
            'login': 'admin',
            'password': 'wrongpassword'
        })
        assert 'Неправильный логин или пароль' in rv.get_data(as_text=True)

    def test_logout(self, client):
        login_user(client, 'admin', 'admin123')
        rv = logout_user(client)
        assert rv.status_code == 200

    def test_registration(self, client):
        rv = client.post('/auth/register', data={
            'login': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'password2': 'newpass123'
        }, follow_redirects=True)
        assert rv.status_code == 200
        assert 'Регистрация успешно завершена' in rv.get_data(as_text=True)

class TestAuthorization:

    def test_admin_can_access_users_list(self, client):
        login_user(client, 'admin', 'admin123')
        rv = client.get('/users/')
        assert rv.status_code == 200
        assert 'Пользователи' in rv.get_data(as_text=True)

    def test_user_cannot_access_users_list(self, client):
        login_user(client, 'testuser', 'test123')
        rv = client.get('/users/')
        assert rv.status_code == 302

        rv = client.get('/users/', follow_redirects=True)
        assert 'У вас нет прав' in rv.get_data(as_text=True)

    def test_admin_can_create_user(self, client):
        login_user(client, 'admin', 'admin123')
        rv = client.get('/users/create')
        assert rv.status_code == 200
        assert 'Создать пользователя' in rv.get_data(as_text=True)

    def test_user_cannot_create_user(self, client):
        login_user(client, 'testuser', 'test123')
        rv = client.get('/users/create', follow_redirects=True)
        assert 'У вас нет прав' in rv.get_data(as_text=True)

    def test_admin_can_edit_any_user(self, client, app):
        login_user(client, 'admin', 'admin123')
        with app.app_context():
            user = User.query.filter_by(login='testuser').first()
            rv = client.get(f'/users/{user.id}/edit')
            assert rv.status_code == 200

    def test_user_can_edit_own_profile(self, client, app):
        login_user(client, 'testuser', 'test123')
        with app.app_context():
            user = User.query.filter_by(login='testuser').first()
            rv = client.get(f'/users/{user.id}/edit')
            assert rv.status_code == 200

    def test_user_cannot_edit_other_users(self, client, app):
        login_user(client, 'testuser', 'test123')
        with app.app_context():
            user = User.query.filter_by(login='another').first()
            rv = client.get(f'/users/{user.id}/edit', follow_redirects=True)
            assert 'У вас нет прав' in rv.get_data(as_text=True)

    def test_admin_can_delete_user(self, client, app):
        login_user(client, 'admin', 'admin123')
        with app.app_context():
            user = User.query.filter_by(login='another').first()
            rv = client.post(f'/users/{user.id}/delete', follow_redirects=True)
            assert rv.status_code == 200

            deleted_user = User.query.filter_by(login='another').first()
            assert deleted_user is None

    def test_user_cannot_delete_user(self, client, app):
        login_user(client, 'testuser', 'test123')
        with app.app_context():
            user = User.query.filter_by(login='another').first()
            rv = client.post(f'/users/{user.id}/delete', follow_redirects=True)
            assert 'У вас нет прав' in rv.get_data(as_text=True)

class TestVisitLogging:

    def test_visit_logged_on_page_access(self, client, app):
        login_user(client, 'testuser', 'test123')

        client.get('/users/profile')
        client.get('/users/profile')
        client.get('/users/change_password')

        with app.app_context():
            user = User.query.filter_by(login='testuser').first()
            visits = VisitLog.query.filter_by(user_id=user.id).all()
            assert len(visits) >= 3

    def test_anonymous_visits_logged(self, client, app):
        client.get('/')
        client.get('/auth/login')

        with app.app_context():
            visits = VisitLog.query.filter_by(user_id=None).all()
            assert len(visits) >= 2

    def test_visit_log_contains_correct_data(self, client, app):
        login_user(client, 'testuser', 'test123')
        client.get('/users/profile')

        with app.app_context():
            user = User.query.filter_by(login='testuser').first()
            visit = VisitLog.query.filter_by(
                user_id=user.id,
                page='/users/profile'
            ).first()

            assert visit is not None
            assert visit.page == '/users/profile'
            assert visit.user_id == user.id
            assert visit.created_at is not None

class TestReports:

    def test_admin_can_access_reports(self, client):
        login_user(client, 'admin', 'admin123')
        rv = client.get('/reports/')
        assert rv.status_code == 200
        assert 'Статистические отчёты' in rv.get_data(as_text=True)

    def test_user_cannot_access_reports(self, client):
        login_user(client, 'testuser', 'test123')
        rv = client.get('/reports/', follow_redirects=True)
        assert 'У вас нет прав' in rv.get_data(as_text=True)

    def test_pages_stats_report(self, client, app):

        login_user(client, 'testuser', 'test123')
        client.get('/users/profile')
        client.get('/users/profile')
        client.get('/users/change_password')

        logout_user(client)
        login_user(client, 'admin', 'admin123')
        rv = client.get('/reports/pages_stats')
        assert rv.status_code == 200
        assert 'Статистика по страницам' in rv.get_data(as_text=True)

    def test_users_stats_report(self, client, app):

        login_user(client, 'testuser', 'test123')
        client.get('/users/profile')
        logout_user(client)

        login_user(client, 'another', 'another123')
        client.get('/users/profile')
        logout_user(client)

        login_user(client, 'admin', 'admin123')
        rv = client.get('/reports/users_stats')
        assert rv.status_code == 200
        assert 'Статистика по пользователям' in rv.get_data(as_text=True)

    def test_csv_export_pages(self, client, app):

        login_user(client, 'testuser', 'test123')
        client.get('/users/profile')
        logout_user(client)

        login_user(client, 'admin', 'admin123')
        rv = client.get('/reports/pages_stats?format=csv')
        assert rv.status_code == 200
        assert rv.headers['Content-Type'] == 'text/csv; charset=utf-8'
        assert 'attachment; filename=pages_stats.csv' in rv.headers['Content-Disposition']

        csv_content = rv.get_data(as_text=True)
        reader = csv.reader(io.StringIO(csv_content))
        rows = list(reader)
        assert len(rows) >= 2
        assert rows[0] == ['Страница', 'Количество посещений']

    def test_csv_export_users(self, client, app):

        login_user(client, 'testuser', 'test123')
        client.get('/users/profile')
        logout_user(client)

        login_user(client, 'admin', 'admin123')
        rv = client.get('/reports/users_stats?format=csv')
        assert rv.status_code == 200
        assert rv.headers['Content-Type'] == 'text/csv; charset=utf-8'
        assert 'attachment; filename=users_stats.csv' in rv.headers['Content-Disposition']

class TestUserManagement:

    def test_create_user_as_admin(self, client, app):
        login_user(client, 'admin', 'admin123')

        with app.app_context():
            role = Role.query.filter_by(name='user').first()

        rv = client.post('/users/create', data={
            'login': 'created_user',
            'first_name': 'Created',
            'last_name': 'User',
            'email': 'created@test.com',
            'password': 'created123',
            'password2': 'created123',
            'role_id': role.id
        }, follow_redirects=True)

        assert rv.status_code == 200
        assert 'Пользователь успешно создан' in rv.get_data(as_text=True)

        with app.app_context():
            created_user = User.query.filter_by(login='created_user').first()
            assert created_user is not None
            assert created_user.email == 'created@test.com'

    def test_edit_user_as_admin(self, client, app):
        login_user(client, 'admin', 'admin123')

        with app.app_context():
            user = User.query.filter_by(login='testuser').first()
            user_id = user.id

        rv = client.post(f'/users/{user_id}/edit', data={
            'login': 'testuser',
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@test.com',
            'role_id': user.role_id
        }, follow_redirects=True)

        assert rv.status_code == 200
        assert 'Данные пользователя обновлены' in rv.get_data(as_text=True)

        with app.app_context():
            updated_user = User.query.get(user_id)
            assert updated_user.first_name == 'Updated'
            assert updated_user.email == 'updated@test.com'

    def test_change_password(self, client, app):
        login_user(client, 'testuser', 'test123')

        rv = client.post('/users/change_password', data={
            'old_password': 'test123',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }, follow_redirects=True)

        assert rv.status_code == 200
        assert 'Пароль успешно изменён' in rv.get_data(as_text=True)

        logout_user(client)
        rv = client.post('/auth/login', data={
            'login': 'testuser',
            'password': 'test123'
        })
        assert 'Неправильный логин или пароль' in rv.get_data(as_text=True)

        rv = login_user(client, 'testuser', 'newpass123')
        assert rv.status_code == 200

class TestUserProfile:

    def test_user_can_view_own_profile(self, client, app):
        login_user(client, 'testuser', 'test123')
        rv = client.get('/users/profile')
        assert rv.status_code == 200
        assert 'testuser' in rv.get_data(as_text=True)
        assert 'Test' in rv.get_data(as_text=True)

    def test_user_can_view_own_visits(self, client, app):
        login_user(client, 'testuser', 'test123')

        client.get('/users/profile')
        client.get('/users/change_password')

        rv = client.get('/users/visits')
        assert rv.status_code == 200
        assert 'Мои посещения' in rv.get_data(as_text=True)

if __name__ == '__main__':
    pytest.main([__file__])
