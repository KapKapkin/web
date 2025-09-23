from flask import Blueprint, render_template, request, make_response, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from app.models import db, VisitLog, User
from app.auth_utils import check_rights
import csv
from io import StringIO

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
@login_required
def index():
    """Главная страница журнала посещений"""
    # Проверяем права доступа
    if not (current_user.has_permission('view_all_visits') or current_user.has_permission('view_own_visits')):
        flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Количество записей на странице
    
    # Для администратора показываем все посещения
    if current_user.has_permission('view_all_visits'):
        visits_query = VisitLog.query
    else:
        # Для обычного пользователя только его посещения
        visits_query = VisitLog.query.filter_by(user_id=current_user.id)
    
    visits = visits_query.order_by(desc(VisitLog.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('reports/index.html', visits=visits)

@reports_bp.route('/pages')
@login_required
@check_rights('view_all_visits')
def pages_report():
    """Отчет по посещениям страниц"""
    # Группируем посещения по страницам и считаем количество
    page_stats = db.session.query(
        VisitLog.path,
        func.count(VisitLog.id).label('visit_count')
    ).group_by(VisitLog.path).order_by(desc('visit_count')).all()
    
    return render_template('reports/pages.html', page_stats=page_stats)

@reports_bp.route('/pages/export')
@login_required
@check_rights('view_all_visits')
def export_pages_csv():
    """Экспорт отчета по страницам в CSV"""
    # Получаем данные
    page_stats = db.session.query(
        VisitLog.path,
        func.count(VisitLog.id).label('visit_count')
    ).group_by(VisitLog.path).order_by(desc('visit_count')).all()
    
    # Создаем CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Заголовки
    writer.writerow(['№', 'Страница', 'Количество посещений'])
    
    # Данные
    for i, (path, count) in enumerate(page_stats, 1):
        writer.writerow([i, path, count])
    
    # Создаем ответ
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=pages_report.csv'
    
    return response

@reports_bp.route('/users')
@login_required
@check_rights('view_all_visits')
def users_report():
    """Отчет по посещениям пользователей"""
    # Считаем посещения для каждого пользователя + неаутентифицированные
    user_stats = db.session.query(
        User.id,
        User.first_name,
        User.last_name,
        User.middle_name,
        func.count(VisitLog.id).label('visit_count')
    ).outerjoin(VisitLog, User.id == VisitLog.user_id)\
     .group_by(User.id, User.first_name, User.last_name, User.middle_name)\
     .order_by(desc('visit_count')).all()
    
    # Считаем неаутентифицированные посещения
    anonymous_count = VisitLog.query.filter_by(user_id=None).count()
    
    return render_template('reports/users.html', 
                         user_stats=user_stats, 
                         anonymous_count=anonymous_count)

@reports_bp.route('/users/export')
@login_required
@check_rights('view_all_visits')
def export_users_csv():
    """Экспорт отчета по пользователям в CSV"""
    # Получаем данные
    user_stats = db.session.query(
        User.id,
        User.first_name,
        User.last_name,
        User.middle_name,
        func.count(VisitLog.id).label('visit_count')
    ).outerjoin(VisitLog, User.id == VisitLog.user_id)\
     .group_by(User.id, User.first_name, User.last_name, User.middle_name)\
     .order_by(desc('visit_count')).all()
    
    # Неаутентифицированные посещения
    anonymous_count = VisitLog.query.filter_by(user_id=None).count()
    
    # Создаем CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Заголовки
    writer.writerow(['№', 'Пользователь', 'Количество посещений'])
    
    # Данные зарегистрированных пользователей
    for i, (user_id, first_name, last_name, middle_name, count) in enumerate(user_stats, 1):
        full_name = ' '.join(filter(None, [last_name, first_name, middle_name]))
        writer.writerow([i, full_name, count])
    
    # Неаутентифицированные пользователи
    if anonymous_count > 0:
        writer.writerow([len(user_stats) + 1, 'Неаутентифицированный пользователь', anonymous_count])
    
    # Создаем ответ
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=users_report.csv'
    
    return response