from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, User, Role
from app.forms import UserForm, UserEditForm

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@main_bp.route('/user/<int:user_id>')
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user/view.html', user=user)

@main_bp.route('/user/create', methods=['GET', 'POST'])
@login_required
def create_user():
    form = UserForm()
    form.role_id.choices = [(r.id, r.name) for r in Role.query.order_by('name')]

    if form.validate_on_submit():
        user = User()
        user.username = form.username.data
        user.last_name = form.last_name.data or ''
        user.first_name = form.first_name.data
        user.middle_name = form.middle_name.data or ''
        user.role_id = form.role_id.data
        user.set_password(form.password.data)

        db.session.add(user)
        try:
            db.session.commit()
            flash('Пользователь успешно создан!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при создании пользователя: ' + str(e), 'error')

    return render_template('user/create.html', form=form)

@main_bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)
    form.role_id.choices = [(r.id, r.name) for r in Role.query.order_by('name')]

    if form.validate_on_submit():
        user.username = form.username.data
        user.last_name = form.last_name.data
        user.first_name = form.first_name.data
        user.middle_name = form.middle_name.data
        user.role_id = form.role_id.data

        if form.password.data:
            user.set_password(form.password.data)

        try:
            db.session.commit()
            flash('Пользователь успешно обновлен!', 'success')
            return redirect(url_for('main.view_user', user_id=user.id))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при обновлении пользователя: ' + str(e), 'error')

    return render_template('user/edit.html', form=form, user=user)

@main_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Вы не можете удалить свою собственную учетную запись!', 'error')
        return redirect(url_for('main.index'))
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Пользователь успешно удален!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении пользователя: ' + str(e), 'error')
    return redirect(url_for('main.index'))

@main_bp.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html')

@main_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    from app.forms import ChangePasswordForm
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Пароль успешно изменен!', 'success')
            return redirect(url_for('main.profile'))
        else:
            flash('Неверный текущий пароль!', 'error')

    return render_template('user/change_password.html', form=form)
