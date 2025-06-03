from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .models import db, User, Role
from .forms import UserForm, UserEditForm

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    users = User.query.all()
    return render_template('user/index.html', users=users)

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
        user = User(
            username=form.username.data,
            last_name=form.last_name.data,
            first_name=form.first_name.data,
            middle_name=form.middle_name.data,
            role_id=form.role_id.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
            flash('User created successfully!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating user: ' + str(e), 'danger')
    
    return render_template('user/create.html', form=form)

@main_bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)
    form.role_id.choices = [(r.id, r.name) for r in Role.query.order_by('name')]
    
    if form.validate_on_submit():
        form.populate_obj(user)
        try:
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('main.view_user', user_id=user.id))
        except Exception as e:
            db.session.rollback()
            flash('Error updating user: ' + str(e), 'danger')
    
    return render_template('user/edit.html', form=form, user=user)

@main_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting user: ' + str(e), 'danger')
    return redirect(url_for('main.index'))