from app import create_app, db
from app.models import User, Role

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Role': Role}

def init_database():
    with app.app_context():
        db.create_all()

        if not Role.query.first():
            admin_role = Role(name='Администратор', description='Полный доступ к системе')
            user_role = Role(name='Пользователь', description='Обычный пользователь')
            manager_role = Role(name='Менеджер', description='Управление пользователями')

            db.session.add(admin_role)
            db.session.add(user_role)
            db.session.add(manager_role)
            db.session.commit()

            admin_user = User(
                username='admin',
                first_name='Админ',
                last_name='Системы',
                role_id=admin_role.id
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()

            print("База данных инициализирована. Создан пользователь admin с паролем admin123")

if __name__ == '__main__':
    init_database()
    app.run(debug=True)
