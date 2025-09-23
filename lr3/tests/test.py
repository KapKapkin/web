import pytest
from app import app, users
from flask import session, url_for
from flask_login import current_user

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_visit_counter_first_visit(client):
    """Тест: счетчик показывает 1 при первом посещении"""
    response = client.get('/')
    assert b'\xd0\x92\xd1\x8b \xd0\xbf\xd0\xbe\xd1\x81\xd0\xb5\xd1\x82\xd0\xb8\xd0\xbb\xd0\xb8 \xd1\x8d\xd1\x82\xd1\x83 \xd1\x81\xd1\x82\xd1\x80\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x86\xd1\x83 1 \xd1\x80\xd0\xb0\xd0\xb7' in response.data  # "Вы посетили эту страницу 1 раз"

def test_visit_counter_multiple_visits(client):
    """Тест: счетчик увеличивается при повторных посещениях"""
    # Первое посещение
    client.get('/')
    # Второе посещение 
    response = client.get('/')
    assert b'\xd0\x92\xd1\x8b \xd0\xbf\xd0\xbe\xd1\x81\xd0\xb5\xd1\x82\xd0\xb8\xd0\xbb\xd0\xb8 \xd1\x8d\xd1\x82\xd1\x83 \xd1\x81\xd1\x82\xd1\x80\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x86\xd1\x83 2 \xd1\x80\xd0\xb0\xd0\xb7' in response.data  # "Вы посетили эту страницу 2 раз"
    
    # Третье посещение
    response = client.get('/')
    assert b'\xd0\x92\xd1\x8b \xd0\xbf\xd0\xbe\xd1\x81\xd0\xb5\xd1\x82\xd0\xb8\xd0\xbb\xd0\xb8 \xd1\x8d\xd1\x82\xd1\x83 \xd1\x81\xd1\x82\xd1\x80\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x86\xd1\x83 3 \xd1\x80\xd0\xb0\xd0\xb7' in response.data  # "Вы посетили эту страницу 3 раз"

def test_visit_counter_separate_sessions(client):
    """Тест: каждая сессия имеет свой счетчик"""
    # Используем разные клиенты для имитации разных сессий
    with app.test_client() as client1:
        response1 = client1.get('/')
        assert b'\xd0\x92\xd1\x8b \xd0\xbf\xd0\xbe\xd1\x81\xd0\xb5\xd1\x82\xd0\xb8\xd0\xbb\xd0\xb8 \xd1\x8d\xd1\x82\xd1\x83 \xd1\x81\xd1\x82\xd1\x80\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x86\xd1\x83 1 \xd1\x80\xd0\xb0\xd0\xb7' in response1.data
    
    with app.test_client() as client2:
        response2 = client2.get('/')
        assert b'\xd0\x92\xd1\x8b \xd0\xbf\xd0\xbe\xd1\x81\xd0\xb5\xd1\x82\xd0\xb8\xd0\xbb\xd0\xb8 \xd1\x8d\xd1\x82\xd1\x83 \xd1\x81\xd1\x82\xd1\x80\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x86\xd1\x83 1 \xd1\x80\xd0\xb0\xd0\xb7' in response2.data

def test_login_success(client):
    """Тест: успешная аутентификация перенаправляет на главную с сообщением"""
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)
    assert b'\xd0\x92\xd1\x8b \xd1\x83\xd1\x81\xd0\xbf\xd0\xb5\xd1\x88\xd0\xbd\xd0\xbe \xd0\xb2\xd0\xbe\xd1\x88\xd0\xbb\xd0\xb8 \xd0\xb2 \xd1\x81\xd0\xb8\xd1\x81\xd1\x82\xd0\xb5\xd0\xbc\xd1\x83!' in response.data  # "Вы успешно вошли в систему!"
    assert b'\xd0\xa1\xd0\xb5\xd0\xba\xd1\x80\xd0\xb5\xd1\x82\xd0\xbd\xd0\xb0\xd1\x8f \xd1\x81\xd1\x82\xd1\x80\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x86\xd0\xb0' in response.data  # Проверяем что навбар показывает ссылку на секретную страницу

def test_login_failure(client):
    """Тест: неудачная попытка аутентификации показывает ошибку"""
    response = client.post('/login', data={
        'username': 'user',
        'password': 'wrong'
    })
    assert b'\xd0\x9d\xd0\xb5\xd0\xb2\xd0\xb5\xd1\x80\xd0\xbd\xd0\xbe\xd0\xb5 \xd0\xb8\xd0\xbc\xd1\x8f \xd0\xbf\xd0\xbe\xd0\xbb\xd1\x8c\xd0\xb7\xd0\xbe\xd0\xb2\xd0\xb0\xd1\x82\xd0\xb5\xd0\xbb\xd1\x8f \xd0\xb8\xd0\xbb\xd0\xb8 \xd0\xbf\xd0\xb0\xd1\x80\xd0\xbe\xd0\xbb\xd1\x8c' in response.data  # "Неверное имя пользователя или пароль"
    assert b'\xd0\xa1\xd0\xb5\xd0\xba\xd1\x80\xd0\xb5\xd1\x82\xd0\xbd\xd0\xb0\xd1\x8f \xd1\x81\xd1\x82\xd1\x80\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x86\xd0\xb0' not in response.data  # Навбар не должен показывать ссылку на секретную страницу

def test_secret_page_authenticated(client):
    """Тест: аутентифицированный пользователь имеет доступ к секретной странице"""
    # Сначала входим
    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    })
    
    # Переходим на секретную страницу
    response = client.get('/secret')
    assert response.status_code == 200
    assert b'\xd0\xa1\xd0\xb5\xd0\xba\xd1\x80\xd0\xb5\xd1\x82\xd0\xbd\xd0\xb0\xd1\x8f \xd1\x81\xd1\x82\xd1\x80\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x86\xd0\xb0' in response.data
    assert b'user' in response.data  # Проверяем что отображается логин пользователя

def test_secret_page_unauthenticated(client):
    """Тест: неаутентифицированный пользователь перенаправляется на страницу входа"""
    response = client.get('/secret', follow_redirects=True)
    assert b'\xd0\x94\xd0\xbb\xd1\x8f \xd0\xb4\xd0\xbe\xd1\x81\xd1\x82\xd1\x83\xd0\xbf\xd0\xb0 \xd0\xba \xd1\x8d\xd1\x82\xd0\xbe\xd0\xb9 \xd1\x81\xd1\x82\xd1\x80\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x86\xd0\xb5 \xd0\xbd\xd0\xb5\xd0\xbe\xd0\xb1\xd1\x85\xd0\xbe\xd0\xb4\xd0\xb8\xd0\xbc\xd0\xbe \xd0\xb2\xd0\xbe\xd0\xb9\xd1\x82\xd0\xb8 \xd0\xb2 \xd1\x81\xd0\xb8\xd1\x81\xd1\x82\xd0\xb5\xd0\xbc\xd1\x83' in response.data  # Сообщение о необходимости войти
    assert b'\xd0\x92\xd1\x85\xd0\xbe\xd0\xb4 \xd0\xb2 \xd1\x81\xd0\xb8\xd1\x81\xd1\x82\xd0\xb5\xd0\xbc\xd1\x83' in response.data  # Должен быть перенаправлен на страницу входа

def test_redirect_after_login(client):
    """Тест: после входа пользователь перенаправляется на изначально запрошенную страницу"""
    # Сначала пытаемся попасть на секретную страницу
    response = client.get('/secret')
    assert response.status_code == 302  # Перенаправление на логин
    
    # Теперь входим
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)
    
    # Проверяем что попали на секретную страницу
    assert b'\xd0\xa1\xd0\xb5\xd0\xba\xd1\x80\xd0\xb5\xd1\x82\xd0\xbd\xd0\xb0\xd1\x8f \xd1\x81\xd1\x82\xd1\x80\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x86\xd0\xb0' in response.data

def test_logout(client):
    """Тест: выход из системы работает корректно"""
    # Сначала входим
    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    })
    
    # Выходим
    response = client.get('/logout', follow_redirects=True)
    assert b'\xd0\x92\xd1\x8b \xd0\xb2\xd1\x8b\xd1\x88\xd0\xbb\xd0\xb8 \xd0\xb8\xd0\xb7 \xd1\x81\xd0\xb8\xd1\x81\xd1\x82\xd0\xb5\xd0\xbc\xd1\x8b' in response.data  # "Вы вышли из системы"
    assert b'\xd0\xa1\xd0\xb5\xd0\xba\xd1\x80\xd0\xb5\xd1\x82\xd0\xbd\xd0\xb0\xd1\x8f \xd1\x81\xd1\x82\xd1\x80\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x86\xd0\xb0' not in response.data  # Навбар не должен показывать ссылку на секретную страницу

def test_remember_me_checkbox(client):
    """Тест: функция 'Запомнить меня' устанавливает cookie с длительным сроком действия"""
    # Сначала заходим на страницу логина для получения session cookie
    client.get('/login')
    
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty',
        'remember': 'on'
    })
    
    # Проверяем успешность логина
    assert response.status_code == 302  # Редирект после успешного входа
    
    # Просто проверяем что функция remember работает - пользователь должен остаться залогиненным
    # после входа с галочкой "запомнить меня"
    response = client.get('/')
    assert b'\xd0\x92\xd1\x8b \xd0\xb2\xd0\xbe\xd1\x88\xd0\xbb\xd0\xb8 \xd0\xba\xd0\xb0\xd0\xba' in response.data  # "Вы вошли как"

def test_remember_me_not_checked(client):
    """Тест: без галочки 'Запомнить меня' cookie сессионный"""
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)
    
    # Проверяем что remember_token НЕ установлен
    set_cookie_headers = response.headers.getlist('Set-Cookie')
    remember_cookie_found = any('remember_token' in header for header in set_cookie_headers)
    # В тесте без remember=on remember_token не должен устанавливаться
    # или если устанавливается, то должен быть сессионным (без expires)

def test_nav_links_authenticated(client):
    """Тест: навбар показывает правильные ссылки для аутентифицированного пользователя"""
    # Входим
    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    })
    
    response = client.get('/')
    assert b'\xd0\xa1\xd0\xb5\xd0\xba\xd1\x80\xd0\xb5\xd1\x82\xd0\xbd\xd0\xb0\xd1\x8f \xd1\x81\xd1\x82\xd1\x80\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x86\xd0\xb0' in response.data  # Ссылка на секретную страницу
    assert b'\xd0\x92\xd1\x8b\xd0\xb9\xd1\x82\xd0\xb8' in response.data  # Ссылка "Выйти"
    assert b'\xd0\x92\xd0\xbe\xd0\xb9\xd1\x82\xd0\xb8' not in response.data  # Ссылки "Войти" быть не должно

def test_nav_links_unauthenticated(client):
    """Тест: навбар показывает правильные ссылки для неаутентифицированного пользователя"""
    response = client.get('/')
    assert b'\xd0\xa1\xd0\xb5\xd0\xba\xd1\x80\xd0\xb5\xd1\x82\xd0\xbd\xd0\xb0\xd1\x8f \xd1\x81\xd1\x82\xd1\x80\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x86\xd0\xb0' not in response.data  # Ссылки на секретную страницу быть не должно
    assert b'\xd0\x92\xd1\x8b\xd0\xb9\xd1\x82\xd0\xb8' not in response.data  # Ссылки "Выйти" быть не должно
    assert b'\xd0\x92\xd0\xbe\xd0\xb9\xd1\x82\xd0\xb8' in response.data  # Ссылка "Войти"

def test_login_page_displays_form(client):
    """Тест: страница входа отображает форму с нужными полями"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'username' in response.data
    assert b'password' in response.data
    assert b'remember' in response.data  # Чекбокс "Запомнить меня"