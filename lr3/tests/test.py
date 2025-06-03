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

def test_visit_counter(client):
    response = client.get('/')
    assert 'Вы посетили эту страницу 0 раз' in str(response.data)
    
    # Second visit
    response = client.get('/')
    assert 'Вы посетили эту страницу 2 раз' in str(response.data)

def test_login_success(client):
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)
    assert 'Вы успешно вошли в систему' in str(response.data)
    assert 'Секретная страница' in str(response.data)  # Check nav shows secret link

def test_login_failure(client):
    response = client.post('/login', data={
        'username': 'user',
        'password': 'wrong'
    })
    assert 'Неверное имя пользователя или пароль' in str(response.data)
    assert 'Секретная страница' not in response.data  # Nav shouldn't show secret link

def test_secret_page_authenticated(client):
    # Login first
    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    })
    
    # Access secret page
    response = client.get('/secret')
    assert 'Секретная страница' in str(response.data)

def test_secret_page_unauthenticated(client):
    response = client.get('/secret', follow_redirects=True)
    assert 'Для доступа к этой странице необходимо войти в систему' in str(response.data)
    assert 'Вход в систему' in str(response.data) # Should be redirected to login

def test_redirect_after_login(client):
    # Try to access secret page first
    client.get('/secret')
    
    # Now login
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)
    
    assert 'Секретная страница' in response.data

def test_logout(client):
    # Login first
    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    })
    
    # Logout
    response = client.get('/logout', follow_redirects=True)
    assert 'Вы вышли из системы' in response.data
    assert 'Секретная страница' not in response.data  # Nav shouldn't show secret link

def test_remember_me(client):
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty',
        'remember': 'on'
    }, follow_redirects=True)
    
    # Check if remember token is set
    assert 'remember_token' in [cookie.name for cookie in client.cookie_jar]
    
    # Check if cookie has max-age set (remember me)
    remember_cookie = next((c for c in client.cookie_jar if c.name == 'remember_token'), None)
    assert remember_cookie is not None
    assert remember_cookie.expires is not None

def test_nav_links_authenticated(client):
    # Login first
    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    })
    
    response = client.get('/')
    assert 'Секретная страница' in response.data
    assert 'Выйти' in response.data
    assert 'Войти' not in response.data

def test_nav_links_unauthenticated(client):
    response = client.get('/')
    assert 'Секретная страница' not in response.data
    assert 'Выйти' not in response.data
    assert 'Войти' in response.data