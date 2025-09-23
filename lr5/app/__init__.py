from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from config import Config
from app.models import db, User, VisitLog
from app.auth_utils import can_user_access, can_edit_user, can_view_user

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates')
    app.config.from_object(config_class)
    
    # Инициализация расширений
    db.init_app(app)
    
    # Настройка Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Для доступа к этой странице необходимо войти в систему.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Регистрация blueprint'ов
    from app.auth import auth_bp
    from app.routes import main_bp
    from app.reports import reports_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    # Добавление функций в контекст шаблонов
    @app.context_processor
    def inject_auth_functions():
        return {
            'can_user_access': can_user_access,
            'can_edit_user': can_edit_user,
            'can_view_user': can_view_user
        }
    
    # Логирование посещений
    @app.before_request
    def log_visit():
        # Исключаем статические файлы и некоторые служебные маршруты
        excluded_paths = ['/static/', '/favicon.ico', '/_debug_toolbar/']
        
        if any(request.path.startswith(path) for path in excluded_paths):
            return
        
        # Создаем запись в журнале посещений
        visit_log = VisitLog(
            page=request.path,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        
        try:
            db.session.add(visit_log)
            db.session.commit()
        except Exception as e:
            # В случае ошибки откатываем транзакцию
            db.session.rollback()
            app.logger.error(f"Ошибка при записи в журнал посещений: {e}")
    
    # Создание таблиц и начальных данных
    with app.app_context():
        db.create_all()
        
        # Создаем роли по умолчанию
        from app.models import Role
        
        if not Role.query.first():
            admin_role = Role(name='Администратор', description='Полный доступ к системе')
            user_role = Role(name='Пользователь', description='Обычный пользователь')
            
            db.session.add(admin_role)
            db.session.add(user_role)
            db.session.commit()
            
            # Создаем администратора по умолчанию
            admin_user = User(
                username='admin',
                first_name='Администратор',
                last_name='Системы',
                role_id=admin_role.id
            )
            admin_user.set_password('admin123')
            
            # Создаем тестового пользователя
            test_user = User(
                username='user',
                first_name='Тестовый',
                last_name='Пользователь',
                role_id=user_role.id
            )
            test_user.set_password('user123')
            
            db.session.add(admin_user)
            db.session.add(test_user)
            db.session.commit()
    
    return app