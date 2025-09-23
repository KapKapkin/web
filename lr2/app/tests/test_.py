import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_cookies_page_set_cookie(client):
    """Тест: cookie устанавливается при первом посещении"""
    response = client.get('/cookies')
    assert response.status_code == 200
    # Проверяем что cookie установился
    assert 'user_visited=yes' in response.headers.get('Set-Cookie', '')

def test_cookies_page_remove_cookie(client):
    """Тест: cookie удаляется при повторном посещении"""
    # Устанавливаем cookie
    client.set_cookie('user_visited', 'yes')
    response = client.get('/cookies')
    assert response.status_code == 200
    # Проверяем что cookie удаляется (expires=0)
    assert 'user_visited=; Expires=' in response.headers.get('Set-Cookie', '')

def test_url_params_display_all(client):
    """Тест: отображаются все переданные параметры URL"""
    response = client.get('/url_params?param1=value1&param2=value2&param3=value3')
    assert response.status_code == 200
    assert b'param1' in response.data
    assert b'value1' in response.data
    assert b'param2' in response.data
    assert b'value2' in response.data
    assert b'param3' in response.data
    assert b'value3' in response.data

def test_url_params_empty(client):
    """Тест: страница работает без параметров"""
    response = client.get('/url_params')
    assert response.status_code == 200
    assert b'URL Parameters' in response.data

def test_headers_display_all(client):
    """Тест: отображаются все заголовки запроса"""
    response = client.get('/headers', headers={
        'Custom-Header': 'TestValue',
        'User-Agent': 'TestAgent'
    })
    assert response.status_code == 200
    assert b'Custom-Header' in response.data
    assert b'TestValue' in response.data
    assert b'User-Agent' in response.data
    assert b'TestAgent' in response.data

def test_form_params_get(client):
    """Тест: GET запрос на форму отображает форму"""
    response = client.get('/form_params')
    assert response.status_code == 200
    assert b'Form Parameters' in response.data
    assert b'<form' in response.data

def test_form_params_post_display_data(client):
    """Тест: POST запрос отображает введенные данные"""
    response = client.post('/form_params', data={
        'name': 'Иван Иванов',
        'email': 'ivan@example.com',
        'additional': 'extra_value'
    })
    assert response.status_code == 200
    assert b'\xd0\x98\xd0\xb2\xd0\xb0\xd0\xbd \xd0\x98\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xbe\xd0\xb2' in response.data  # Иван Иванов в UTF-8
    assert b'ivan@example.com' in response.data
    assert b'additional' in response.data
    assert b'extra_value' in response.data

def test_phone_page_get(client):
    """Тест: GET запрос отображает форму валидации"""
    response = client.get('/phone')
    assert response.status_code == 200
    assert b'Phone Validation' in response.data
    assert b'Examples' in response.data

def test_phone_valid_formats(client):
    """Тест: валидные форматы номеров"""
    valid_phones = [
        '+7 (123) 456-75-90',
        '8(123)4567590',
        '123.456.75.90',
        '+7 123 456 75 90',
        '8 123 456 75 90'
    ]
    
    for phone in valid_phones:
        response = client.post('/phone', data={'phone': phone})
        assert response.status_code == 200
        assert b'8-123-456-75-90' in response.data
        assert b'is-invalid' not in response.data

def test_phone_invalid_chars_error(client):
    """Тест: ошибка при недопустимых символах"""
    response = client.post('/phone', data={'phone': '123#456$75@90'})
    assert response.status_code == 200
    assert b'is-invalid' in response.data
    assert '\u041d\u0435\u0434\u043e\u043f\u0443\u0441\u0442\u0438\u043c\u044b\u0439 \u0432\u0432\u043e\u0434. \u0412 \u043d\u043e\u043c\u0435\u0440\u0435 \u0442\u0435\u043b\u0435\u0444\u043e\u043d\u0430 \u0432\u0441\u0442\u0440\u0435\u0447\u0430\u044e\u0442\u0441\u044f \u043d\u0435\u0434\u043e\u043f\u0443\u0441\u0442\u0438\u043c\u044b\u0435 \u0441\u0438\u043c\u0432\u043e\u043b\u044b.'.encode('utf-8') in response.data

def test_phone_invalid_length_plus7(client):
    """Тест: ошибка длины для номеров с +7"""
    response = client.post('/phone', data={'phone': '+7 (123) 456-75'})
    assert response.status_code == 200
    assert b'is-invalid' in response.data
    assert '\u041d\u0435\u0434\u043e\u043f\u0443\u0441\u0442\u0438\u043c\u044b\u0439 \u0432\u0432\u043e\u0434. \u041d\u0435\u0432\u0435\u0440\u043d\u043e\u0435 \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0446\u0438\u0444\u0440.'.encode('utf-8') in response.data

def test_phone_invalid_length_8_prefix(client):
    """Тест: ошибка длины для номеров с 8"""
    response = client.post('/phone', data={'phone': '8 (123) 456-75'})
    assert response.status_code == 200
    assert b'is-invalid' in response.data
    assert '\u041d\u0435\u0434\u043e\u043f\u0443\u0441\u0442\u0438\u043c\u044b\u0439 \u0432\u0432\u043e\u0434. \u041d\u0435\u0432\u0435\u0440\u043d\u043e\u0435 \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0446\u0438\u0444\u0440.'.encode('utf-8') in response.data

def test_phone_invalid_length_no_prefix(client):
    """Тест: ошибка длины для номеров без префикса"""
    response = client.post('/phone', data={'phone': '123-456-75'})
    assert response.status_code == 200
    assert b'is-invalid' in response.data
    assert '\u041d\u0435\u0434\u043e\u043f\u0443\u0441\u0442\u0438\u043c\u044b\u0439 \u0432\u0432\u043e\u0434. \u041d\u0435\u0432\u0435\u0440\u043d\u043e\u0435 \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0446\u0438\u0444\u0440.'.encode('utf-8') in response.data

def test_phone_bootstrap_classes_on_error(client):
    """Тест: использование Bootstrap классов при ошибке"""
    response = client.post('/phone', data={'phone': 'invalid'})
    assert response.status_code == 200
    assert b'is-invalid' in response.data
    assert b'invalid-feedback' in response.data

def test_phone_formatted_output(client):
    """Тест: корректное форматирование номера"""
    response = client.post('/phone', data={'phone': '1234567890'})
    assert response.status_code == 200
    assert b'8-123-456-78-90' in response.data

def test_phone_preserves_input_on_error(client):
    """Тест: сохранение введенного значения при ошибке"""
    test_phone = '123#invalid'
    response = client.post('/phone', data={'phone': test_phone})
    assert response.status_code == 200
    assert test_phone.encode() in response.data

def test_phone_edge_case_11_digits_no_prefix(client):
    """Тест: 11 цифр без префикса +7/8 - ошибка"""
    response = client.post('/phone', data={'phone': '12345678901'})
    assert response.status_code == 200
    assert b'is-invalid' in response.data

def test_phone_valid_long_format_plus7(client):
    """Тест: длинный формат с +7"""
    response = client.post('/phone', data={'phone': '+7 (123) 456-78-90'})
    assert response.status_code == 200
    assert b'8-123-456-78-90' in response.data
    assert b'is-invalid' not in response.data