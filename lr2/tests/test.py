import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_cookies_page(client):
    response = client.get('/cookies')
    assert b'visited' not in response.data

    response = client.get('/cookies')
    assert b'visited' in response.data
    assert b'yes' in response.data

def test_url_params_page(client):
    response = client.get('/url_params?test1=value1&test2=value2')
    assert b'test1' in response.data
    assert b'value1' in response.data
    assert b'test2' in response.data
    assert b'value2' in response.data

def test_headers_page(client):
    response = client.get('/headers')
    assert b'Headers' in response.data
    assert b'User-Agent' in response.data

def test_form_params_page_get(client):
    response = client.get('/form_params')
    assert b'Form Parameters' in response.data
    assert b'Name' in response.data
    assert b'Email' in response.data

def test_form_params_page_post(client):
    response = client.post('/form_params', data={
        'name': 'Test User',
        'email': 'test@example.com'
    })
    assert b'Test User' in response.data
    assert b'test@example.com' in response.data

def test_phone_page_get(client):
    response = client.get('/phone')
    assert b'Phone Validation' in response.data
    assert b'Examples' in response.data

def test_phone_valid_with_plus7(client):
    response = client.post('/phone', data={
        'phone': '+7 (123) 456-75-90'
    })
    assert b'8-123-456-75-90' in response.data
    assert b'is-invalid' not in response.data

def test_phone_valid_with_8(client):
    response = client.post('/phone', data={
        'phone': '8(123)4567590'
    })
    assert b'8-123-456-75-90' in response.data
    assert b'is-invalid' not in response.data

def test_phone_valid_without_prefix(client):
    response = client.post('/phone', data={
        'phone': '123.456.75.90'
    })
    assert b'8-123-456-75-90' in response.data
    assert b'is-invalid' not in response.data

def test_phone_invalid_chars(client):
    response = client.post('/phone', data={
        'phone': '123#456$75@90'
    })
    assert b'8-123-456-75-90' not in response.data
    assert b'is-invalid' in response.data
    assert b'Invalid phone number. Invalid symbols!' in response.data

def test_phone_invalid_length_short(client):
    response = client.post('/phone', data={
        'phone': '+7 (123) 456-75'
    })
    assert b'8-123-456-75' not in response.data
    assert b'is-invalid' in response.data
    assert b'Invalid phone number. Invalid length!' in response.data

def test_phone_invalid_length_long(client):
    response = client.post('/phone', data={
        'phone': '+7 (123) 456-75-90-123'
    })
    assert b'is-invalid' in response.data
    assert b'Invalid phone number. Invalid length!' in response.data

def test_phone_invalid_length_10_digits_with_8(client):
    response = client.post('/phone', data={
        'phone': '8 (123) 456-75'
    })
    assert b'is-invalid' in response.data
    assert b'Invalid phone number. Invalid length!' in response.data

def test_phone_invalid_length_11_digits_without_prefix(client):
    response = client.post('/phone', data={
        'phone': '12345678901'
    })
    assert b'is-invalid' in response.data
    assert b'Invalid phone number. Invalid length!' in response.data

def test_phone_preserves_input_on_error(client):
    test_phone = '123#456$75@90'
    response = client.post('/phone', data={
        'phone': test_phone
    })
    assert test_phone.encode() in response.data
