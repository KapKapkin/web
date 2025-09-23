from functools import wraps
from flask import redirect, url_for, flash, current_app
from flask_login import current_user

def check_rights(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Для доступа к этой странице необходимо войти в систему.', 'warning')
                return redirect(url_for('auth.login'))

            if not current_user.has_permission(permission):
                flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
                return redirect(url_for('main.index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def can_user_access(permission):
    if not current_user.is_authenticated:
        return False
    return current_user.has_permission(permission)

def can_edit_user(user_id):
    if not current_user.is_authenticated:
        return False

    if current_user.has_permission('edit_user'):
        return True

    if current_user.has_permission('edit_own_profile') and current_user.id == int(user_id):
        return True

    return False

def can_view_user(user_id):
    if not current_user.is_authenticated:
        return False

    if current_user.has_permission('view_user'):
        return True

    if current_user.has_permission('view_own_profile') and current_user.id == int(user_id):
        return True

    return False
