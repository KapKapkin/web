from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, User, Role
from app.forms import UserForm, UserEditForm, ChangePasswordForm
from app.auth_utils import check_rights, can_edit_user, can_view_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated and current_user.has_permission('view_user'):
        # Администратор видит всех пользователей
        users = User.query.all()
        return render_template('users/index.html', users=users)
    elif current_user.is_authenticated:
        # Обычный пользователь видит только свой профиль
        return redirect(url_for('main.profile', user_id=current_user.id))
    else:
        # Неаутентифицированный пользователь
        return render_template('index.html')

@main_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@check_rights('create_user')
def create_user():
    form = UserForm()
    
    # Заполняем список ролей
    roles = Role.query.all()
    form.role_id.choices = [(role.id, role.name) for role in roles]
    
    if form.validate_on_submit():
        # Проверяем уникальность имени пользователя
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Пользователь с таким именем уже существует.', 'danger')
            return render_template('users/create.html', form=form)
        
        user = User(
            username=form.username.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            middle_name=form.middle_name.data,
            role_id=form.role_id.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Пользователь {user.full_name} успешно создан.', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('users/create.html', form=form)

@main_bp.route('/users/<int:user_id>')
@login_required
def view_user(user_id):
    if not can_view_user(user_id):
        flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    return render_template('users/view.html', user=user)

@main_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not can_edit_user(user_id):
        flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)
    
    # Заполняем список ролей
    roles = Role.query.all()
    form.role_id.choices = [(role.id, role.name) for role in roles]
    
    # Для обычных пользователей отключаем поле роли
    if not current_user.has_permission('edit_user'):
        form.role_id.render_kw = {'disabled': True}
        form.role_id.data = user.role_id
    
    if form.validate_on_submit():
        # Проверяем уникальность имени пользователя (кроме текущего)
        existing_user = User.query.filter(
            User.username == form.username.data,
            User.id != user_id
        ).first()
        if existing_user:
            flash('Пользователь с таким именем уже существует.', 'danger')
            return render_template('users/edit.html', form=form, user=user)
        
        user.username = form.username.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.middle_name = form.middle_name.data
        
        # Обычные пользователи не могут менять свою роль
        if current_user.has_permission('edit_user'):
            user.role_id = form.role_id.data
        
        db.session.commit()
        flash('Данные пользователя успешно обновлены.', 'success')
        return redirect(url_for('main.view_user', user_id=user.id))
    
    return render_template('users/edit.html', form=form, user=user)

@main_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@check_rights('delete_user')
def delete_user(user_id):
    if user_id == current_user.id:
        flash('Нельзя удалить свою собственную учетную запись.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    username = user.username
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Пользователь {username} успешно удален.', 'success')
    return redirect(url_for('main.index'))

@main_bp.route('/profile')
@main_bp.route('/profile/<int:user_id>')
@login_required
def profile(user_id=None):
    if user_id is None:
        user_id = current_user.id
    
    if not can_view_user(user_id):
        flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    return render_template('users/profile.html', user=user)

@main_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash('Неверный текущий пароль.', 'danger')
            return render_template('users/change_password.html', form=form)
        
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        flash('Пароль успешно изменен.', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('users/change_password.html', form=form)