from flask import Flask, render_template, request, make_response, redirect, url_for
import re

app = Flask(__name__,
           template_folder='templates')

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

    if 'user_visited' not in request.cookies:
        resp.set_cookie('user_visited', 'yes')
    else:

        resp.set_cookie('user_visited', '', expires=0)

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

        allowed_pattern = r'^[\d\s\(\)\-\.\+]*$'
        if not re.match(allowed_pattern, phone_number):
            error = {
                'message': 'Invalid phone number. Invalid symbols!',
                'type': 'invalid_chars'
            }
        else:

            digits = re.sub(r'\D', '', phone_number)

            if phone_number.strip().startswith(('+7', '8')):

                if len(digits) != 11:
                    error = {
                        'message': 'Invalid phone number. Invalid length!',
                        'type': 'invalid_length'
                    }
                else:

                    digits = digits[-10:]
                    formatted_phone = f"8-{digits[:3]}-{digits[3:6]}-{digits[6:8]}-{digits[8:]}"
            else:

                if len(digits) != 10:
                    error = {
                        'message': 'Invalid phone number. Invalid length!',
                        'type': 'invalid_length'
                    }
                else:
                    formatted_phone = f"8-{digits[:3]}-{digits[3:6]}-{digits[6:8]}-{digits[8:]}"

    return render_template(
        'phone_form.html',
        error=error,
        formatted_phone=formatted_phone,
        prev_value=request.form.get('phone', '') if request.method == 'POST' else ''
    )

if __name__ == "__main__":
    app.run(debug=True)
