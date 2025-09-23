import pytest
import tempfile
import os
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Role, VisitLog
from app.auth_utils import check_rights
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for
from flask_login import login_user, current_user


@pytest.fixture
def app():
    """Создаёт тестовое приложение"""
    db_fd, db_path = tempfile.mkstemp()
    
    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
        SECRET_KEY = 'test-secret-key'
        WTF_CSRF_ENABLED = False
    
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        # Создаём роли
        admin_role = Role(name='admin')
        user_role = Role(name='user')
        db.session.add(admin_role)
        db.session.add(user_role)
        db.session.commit()
    
    yield app
    
    os.close(db_fd)
    os.unlink(db_path)


class TestModels:
    """Тесты моделей данных"""
    
    def test_role_creation(self, app):
        """Тест создания роли"""
        with app.app_context():
            role = Role(name='test_role')
            db.session.add(role)
            db.session.commit()
            
            assert role.id is not None
            assert role.name == 'test_role'
            assert str(role) == 'test_role'
    
    def test_user_creation(self, app):
        """Тест создания пользователя"""
        with app.app_context():
            role = Role.query.filter_by(name='user').first()
            
            user = User(
                login='testuser',
                first_name='Test',
                last_name='User',
                email='test@example.com',
                password_hash=generate_password_hash('password123'),
                role=role
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.login == 'testuser'
            assert user.email == 'test@example.com'
            assert user.role.name == 'user'
            assert str(user) == 'testuser'
    
    def test_user_check_password(self, app):
        """Тест проверки пароля пользователя"""
        with app.app_context():
            role = Role.query.filter_by(name='user').first()
            
            user = User(
                login='testuser',
                first_name='Test',
                last_name='User',
                email='test@example.com',
                role=role
            )
            user.set_password('mypassword')
            
            assert user.check_password('mypassword') is True
            assert user.check_password('wrongpassword') is False
    
    def test_user_permissions(self, app):
        """Тест системы прав пользователей"""
        with app.app_context():
            admin_role = Role.query.filter_by(name='admin').first()
            user_role = Role.query.filter_by(name='user').first()
            
            admin_user = User(
                login='admin',
                first_name='Admin',
                last_name='User',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role=admin_role
            )
            
            regular_user = User(
                login='user',
                first_name='Regular',
                last_name='User',
                email='user@example.com',
                password_hash=generate_password_hash('user123'),
                role=user_role
            )
            
            db.session.add(admin_user)
            db.session.add(regular_user)
            db.session.commit()
            
            # Тесты прав администратора
            assert admin_user.has_permission('view_users') is True
            assert admin_user.has_permission('create_users') is True
            assert admin_user.has_permission('edit_users') is True
            assert admin_user.has_permission('delete_users') is True
            assert admin_user.has_permission('view_reports') is True
            
            # Тесты прав обычного пользователя
            assert regular_user.has_permission('view_users') is False
            assert regular_user.has_permission('create_users') is False
            assert regular_user.has_permission('edit_users') is False
            assert regular_user.has_permission('delete_users') is False
            assert regular_user.has_permission('view_reports') is False
            
            # Права, которые есть у всех
            assert regular_user.has_permission('edit_profile') is True
            assert regular_user.has_permission('view_profile') is True
    
    def test_visit_log_creation(self, app):
        """Тест создания записи журнала посещений"""
        with app.app_context():
            role = Role.query.filter_by(name='user').first()
            user = User(
                login='testuser',
                first_name='Test',
                last_name='User',
                email='test@example.com',
                password_hash=generate_password_hash('password123'),
                role=role
            )
            db.session.add(user)
            db.session.commit()
            
            visit = VisitLog(
                page='/test/page',
                user=user
            )
            db.session.add(visit)
            db.session.commit()
            
            assert visit.id is not None
            assert visit.page == '/test/page'
            assert visit.user_id == user.id
            assert visit.created_at is not None
            assert isinstance(visit.created_at, datetime)
    
    def test_visit_log_anonymous_user(self, app):
        """Тест записи журнала для анонимного пользователя"""
        with app.app_context():
            visit = VisitLog(
                page='/public/page',
                user_id=None
            )
            db.session.add(visit)
            db.session.commit()
            
            assert visit.id is not None
            assert visit.page == '/public/page'
            assert visit.user_id is None
            assert visit.user_display_name == 'Анонимный пользователь'
    
    def test_visit_log_user_display_name(self, app):
        """Тест отображаемого имени пользователя в журнале"""
        with app.app_context():
            role = Role.query.filter_by(name='user').first()
            user = User(
                login='testuser',
                first_name='Иван',
                last_name='Петров',
                email='ivan@example.com',
                password_hash=generate_password_hash('password123'),
                role=role
            )
            db.session.add(user)
            db.session.commit()
            
            visit = VisitLog(
                page='/test/page',
                user=user
            )
            db.session.add(visit)
            db.session.commit()
            
            assert visit.user_display_name == 'Иван Петров (testuser)'


class TestAuthUtils:
    """Тесты утилит авторизации"""
    
    def test_check_rights_decorator_with_admin(self, app):
        """Тест декоратора check_rights с администратором"""
        with app.app_context():
            admin_role = Role.query.filter_by(name='admin').first()
            admin_user = User(
                login='admin',
                first_name='Admin',
                last_name='User',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role=admin_role
            )
            db.session.add(admin_user)
            db.session.commit()
            
            @check_rights('view_users')
            def test_view():
                return 'Success'
            
            with app.test_request_context():
                login_user(admin_user)
                result = test_view()
                assert result == 'Success'
    
    def test_check_rights_decorator_insufficient_rights(self, app):
        """Тест декоратора check_rights с недостаточными правами"""
        with app.app_context():
            user_role = Role.query.filter_by(name='user').first()
            regular_user = User(
                login='user',
                first_name='Regular',
                last_name='User',
                email='user@example.com',
                password_hash=generate_password_hash('user123'),
                role=user_role
            )
            db.session.add(regular_user)
            db.session.commit()
            
            @check_rights('view_users')
            def test_view():
                return 'Success'
            
            with app.test_request_context():
                login_user(regular_user)
                result = test_view()
                # Должен возвращать redirect response
                assert result.status_code == 302
    
    def test_check_rights_decorator_unauthenticated(self, app):
        """Тест декоратора check_rights с неаутентифицированным пользователем"""
        @check_rights('view_users')
        def test_view():
            return 'Success'
        
        with app.test_request_context():
            result = test_view()
            # Должен возвращать redirect response
            assert result.status_code == 302


class TestPermissionHelpers:
    """Тесты вспомогательных функций для проверки прав"""
    
    def test_can_user_access_function(self, app):
        """Тест функции can_user_access"""
        with app.app_context():
            admin_role = Role.query.filter_by(name='admin').first()
            user_role = Role.query.filter_by(name='user').first()
            
            admin_user = User(
                login='admin',
                first_name='Admin',
                last_name='User',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role=admin_role
            )
            
            regular_user = User(
                login='user',
                first_name='Regular',
                last_name='User',
                email='user@example.com',
                password_hash=generate_password_hash('user123'),
                role=user_role
            )
            
            db.session.add(admin_user)
            db.session.add(regular_user)
            db.session.commit()
            
            # Имитируем импорт функции из контекстного процессора
            from app.auth_utils import can_user_access
            
            with app.test_request_context():
                login_user(admin_user)
                assert can_user_access('view_users') is True
                assert can_user_access('create_users') is True
            
            with app.test_request_context():
                login_user(regular_user)
                assert can_user_access('view_users') is False
                assert can_user_access('edit_profile') is True
    
    def test_can_edit_user_function(self, app):
        """Тест функции can_edit_user"""
        with app.app_context():
            admin_role = Role.query.filter_by(name='admin').first()
            user_role = Role.query.filter_by(name='user').first()
            
            admin_user = User(
                login='admin',
                first_name='Admin',
                last_name='User',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role=admin_role
            )
            
            user1 = User(
                login='user1',
                first_name='User',
                last_name='One',
                email='user1@example.com',
                password_hash=generate_password_hash('user123'),
                role=user_role
            )
            
            user2 = User(
                login='user2',
                first_name='User',
                last_name='Two',
                email='user2@example.com',
                password_hash=generate_password_hash('user123'),
                role=user_role
            )
            
            db.session.add(admin_user)
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            
            from app.auth_utils import can_edit_user
            
            # Администратор может редактировать любого
            with app.test_request_context():
                login_user(admin_user)
                assert can_edit_user(user1) is True
                assert can_edit_user(user2) is True
            
            # Пользователь может редактировать только себя
            with app.test_request_context():
                login_user(user1)
                assert can_edit_user(user1) is True
                assert can_edit_user(user2) is False
    
    def test_can_view_user_function(self, app):
        """Тест функции can_view_user"""
        with app.app_context():
            admin_role = Role.query.filter_by(name='admin').first()
            user_role = Role.query.filter_by(name='user').first()
            
            admin_user = User(
                login='admin',
                first_name='Admin',
                last_name='User',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role=admin_role
            )
            
            user1 = User(
                login='user1',
                first_name='User',
                last_name='One',
                email='user1@example.com',
                password_hash=generate_password_hash('user123'),
                role=user_role
            )
            
            user2 = User(
                login='user2',
                first_name='User',
                last_name='Two',
                email='user2@example.com',
                password_hash=generate_password_hash('user123'),
                role=user_role
            )
            
            db.session.add(admin_user)
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            
            from app.auth_utils import can_view_user
            
            # Администратор может просматривать любого
            with app.test_request_context():
                login_user(admin_user)
                assert can_view_user(user1) is True
                assert can_view_user(user2) is True
            
            # Пользователь может просматривать только себя
            with app.test_request_context():
                login_user(user1)
                assert can_view_user(user1) is True
                assert can_view_user(user2) is False


class TestDatabaseConstraints:
    """Тесты ограничений базы данных"""
    
    def test_unique_user_login(self, app):
        """Тест уникальности логина пользователя"""
        with app.app_context():
            role = Role.query.filter_by(name='user').first()
            
            user1 = User(
                login='duplicate',
                first_name='User',
                last_name='One',
                email='user1@example.com',
                password_hash=generate_password_hash('password123'),
                role=role
            )
            
            user2 = User(
                login='duplicate',  # Дублирующийся логин
                first_name='User',
                last_name='Two',
                email='user2@example.com',
                password_hash=generate_password_hash('password123'),
                role=role
            )
            
            db.session.add(user1)
            db.session.commit()
            
            db.session.add(user2)
            with pytest.raises(Exception):  # Должно быть исключение при попытке сохранить
                db.session.commit()
    
    def test_unique_user_email(self, app):
        """Тест уникальности email пользователя"""
        with app.app_context():
            role = Role.query.filter_by(name='user').first()
            
            user1 = User(
                login='user1',
                first_name='User',
                last_name='One',
                email='duplicate@example.com',
                password_hash=generate_password_hash('password123'),
                role=role
            )
            
            user2 = User(
                login='user2',
                first_name='User',
                last_name='Two',
                email='duplicate@example.com',  # Дублирующийся email
                password_hash=generate_password_hash('password123'),
                role=role
            )
            
            db.session.add(user1)
            db.session.commit()
            
            db.session.add(user2)
            with pytest.raises(Exception):  # Должно быть исключение при попытке сохранить
                db.session.commit()


class TestPasswordHashing:
    """Тесты хеширования паролей"""
    
    def test_password_hashing(self, app):
        """Тест хеширования и проверки паролей"""
        password = 'mysecretpassword'
        hashed = generate_password_hash(password)
        
        # Хеш не должен быть равен исходному паролю
        assert hashed != password
        
        # Проверка правильного пароля
        assert check_password_hash(hashed, password) is True
        
        # Проверка неправильного пароля
        assert check_password_hash(hashed, 'wrongpassword') is False
    
    def test_user_password_methods(self, app):
        """Тест методов пароля у модели User"""
        with app.app_context():
            role = Role.query.filter_by(name='user').first()
            user = User(
                login='testuser',
                first_name='Test',
                last_name='User',
                email='test@example.com',
                role=role
            )
            
            password = 'testpassword123'
            user.set_password(password)
            
            # Проверяем, что пароль хешируется
            assert user.password_hash != password
            assert user.password_hash is not None
            
            # Проверяем методы проверки пароля
            assert user.check_password(password) is True
            assert user.check_password('wrongpassword') is False


if __name__ == '__main__':
    pytest.main([__file__])