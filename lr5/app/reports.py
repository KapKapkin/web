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

    if not (current_user.has_permission('view_all_visits') or current_user.has_permission('view_own_visits')):
        flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    per_page = 20

    if current_user.has_permission('view_all_visits'):
        visits_query = VisitLog.query
    else:

        visits_query = VisitLog.query.filter_by(user_id=current_user.id)

    visits = visits_query.order_by(desc(VisitLog.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('reports/index.html', visits=visits)

@reports_bp.route('/pages')
@login_required
@check_rights('view_all_visits')
def pages_report():

    page_stats = db.session.query(
        VisitLog.page,
        func.count(VisitLog.id).label('visit_count')
    ).group_by(VisitLog.page).order_by(desc('visit_count')).all()

    return render_template('reports/pages_stats.html', page_stats=page_stats)

@reports_bp.route('/pages/export')
@login_required
@check_rights('view_all_visits')
def export_pages_csv():

    page_stats = db.session.query(
        VisitLog.page,
        func.count(VisitLog.id).label('visit_count')
    ).group_by(VisitLog.page).order_by(desc('visit_count')).all()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(['№', 'Страница', 'Количество посещений'])

    for i, (page, count) in enumerate(page_stats, 1):
        writer.writerow([i, page, count])

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=pages_report.csv'

    return response

@reports_bp.route('/users')
@login_required
@check_rights('view_all_visits')
def users_report():

    user_stats = db.session.query(
        User.id,
        User.first_name,
        User.last_name,
        User.middle_name,
        func.count(VisitLog.id).label('visit_count')
    ).outerjoin(VisitLog, User.id == VisitLog.user_id)\
     .group_by(User.id, User.first_name, User.last_name, User.middle_name)\
     .order_by(desc('visit_count')).all()

    anonymous_count = VisitLog.query.filter_by(user_id=None).count()

    return render_template('reports/users_stats.html',
                         user_stats=user_stats,
                         anonymous_count=anonymous_count)

@reports_bp.route('/users/export')
@login_required
@check_rights('view_all_visits')
def export_users_csv():

    user_stats = db.session.query(
        User.id,
        User.first_name,
        User.last_name,
        User.middle_name,
        func.count(VisitLog.id).label('visit_count')
    ).outerjoin(VisitLog, User.id == VisitLog.user_id)\
     .group_by(User.id, User.first_name, User.last_name, User.middle_name)\
     .order_by(desc('visit_count')).all()

    anonymous_count = VisitLog.query.filter_by(user_id=None).count()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(['№', 'Пользователь', 'Количество посещений'])

    for i, (user_id, first_name, last_name, middle_name, count) in enumerate(user_stats, 1):
        full_name = ' '.join(filter(None, [last_name, first_name, middle_name]))
        writer.writerow([i, full_name, count])

    if anonymous_count > 0:
        writer.writerow([len(user_stats) + 1, 'Неаутентифицированный пользователь', anonymous_count])

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=users_report.csv'

    return response
