from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    users = db.relationship('User', backref='role', lazy=True)
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(50))
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связь с журналом посещений
    visit_logs = db.relationship('VisitLog', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        parts = [self.last_name, self.first_name, self.middle_name]
        return ' '.join(part for part in parts if part)
    
    def has_permission(self, permission):
        """Проверка прав пользователя"""
        if not self.role:
            return False
            
        role_permissions = {
            'Администратор': [
                'create_user', 'edit_user', 'view_user', 'delete_user',
                'view_all_visits', 'view_reports'
            ],
            'Пользователь': [
                'edit_own_profile', 'view_own_profile', 'view_own_visits'
            ]
        }
        
        return permission in role_permissions.get(self.role.name, [])
    
    def __repr__(self):
        return f'<User {self.username}>'

class VisitLog(db.Model):
    __tablename__ = 'visit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def user_display_name(self):
        """Возвращает отображаемое имя пользователя"""
        if self.user:
            return self.user.full_name
        return "Неаутентифицированный пользователь"
    
    def __repr__(self):
        return f'<VisitLog {self.page} by {self.user_display_name}>'