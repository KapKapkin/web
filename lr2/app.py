from flask import Flask, render_template, request, make_response, redirect, url_for
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/url_params')
def url_params():
    return render_template('url_params.html', params=request.args)

@app.route('/headers')
def headers():
    return render_template('headers.html', headers=request.headers)

@app.route('/cookies')
def cookies():
    resp = make_response(render_template('cookies.html', cookies=request.cookies))
    if 'visited' not in request.cookies:
        resp.set_cookie('visited', 'yes')
    else:
        resp.set_cookie('visited', '', expires=0)
    return resp

@app.route('/form_params', methods=['GET', 'POST'])
def form_params():
    if request.method == 'POST':
        return render_template('form_params.html', form_data=request.form)
    return render_template('form_params.html')

@app.route('/phone', methods=['GET', 'POST'])
def phone():
    error = None
    formatted_phone = None
    
    if request.method == 'POST':
        phone_number = request.form.get('phone', '')
        
        # Удаляем все нецифровые символы кроме +, (, ), -, ., пробелов
        cleaned = re.sub(r'[^\d\(\)\-\+\.\s]', '', phone_number)
        digits = re.sub(r'\D', '', phone_number)
        
        # Проверка на недопустимые символы
        if len(cleaned) != len(phone_number):
            error = {
                'message': 'Invalid phone number. Invalid symbols!',
                'type': 'invalid_chars'
            }
        # Проверка длины
        elif phone_number.startswith(('+7', '8')) and len(digits) != 11:
            error = {
                'message': 'Invalid phone number. Invalid length!',
                'type': 'invalid_length'
            }
        elif not phone_number.startswith(('+7', '8')) and len(digits) != 10:
            error = {
                'message': 'Invalid phone number. Invalid length!',
                'type': 'invalid_length'
            }
        else:
            # Форматирование номера
            digits = digits[-10:]  # Берем последние 10 цифр
            formatted_phone = f"8-{digits[:3]}-{digits[3:6]}-{digits[6:8]}-{digits[8:]}"
    
    return render_template(
        'phone_form.html',
        error=error,
        formatted_phone=formatted_phone,
        prev_value=request.form.get('phone', '')
    )

if __name__ == "__main__":
    app.run(debug=True)