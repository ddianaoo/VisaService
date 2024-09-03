import os
import secrets
import requests

from flask import Flask, request, render_template, url_for, redirect, session, flash

from forms import SignUpForm, LoginForm, ExtendVisaForm, RestoreVisaForm, CreateVisaForm
from utils import login_required


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
BASE_URL = os.environ.get("BASE_URL")


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()

    if request.method == "POST":
        if form.validate_on_submit():
            data = {
            "name": form.name.data,
            "surname": form.surname.data,
            "patronymic": form.patronymic.data,
            "email": form.email.data,
            "password": form.password.data,
            "re_password": form.re_password.data,
            "sex": form.sex.data,
            "date_of_birth": form.date_of_birth.data,
            "place_of_birth": form.place_of_birth.data,
            "nationality": form.nationality.data
            }

            url = f"{BASE_URL}/api/auth/users/"
            resp = requests.post(url, data=data, timeout=10)
            if resp.status_code == 201:
                flash('Ви успішно створили обліковий запис.', 'success')
                return redirect(url_for('home'))
            else:
                for errors in resp.json().values():
                    for error in errors:
                        flash(error, 'danger')

    return render_template('signup.html', form=form, title="Реєстрація", session=session)


@app.route('/')
@app.route('/home/')
def home():
    return render_template('home.html', title="Головна сторінка", session=session)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == "POST":
        if form.validate_on_submit():
            data = {
            "email": form.email.data,
            "password": form.password.data,
            }
            login_url = f"{BASE_URL}/api/auth/token/login/"
            resp = requests.post(login_url, data=data, timeout=10)
            if resp.status_code == 200:
                auth_token = resp.json().get('auth_token')
                session['auth_token'] = auth_token
                flash('Ви успішно увійшли в обліковий запис.', 'success')
                return redirect(url_for('home'))
            else:
                for errors in resp.json().values():
                    for error in errors:
                        flash(error, 'danger')

    return render_template('login_page.html', form=form, title="Вхід", session=session)


@app.route('/logout/')
@login_required
def logout():
    session.pop('auth_token', None)
    flash('Ви вийшли з облікового запису.', 'success')
    return redirect(url_for('login'))


@app.route('/my-visas/', methods=['GET', 'POST'])
@login_required
def get_visas():
    url = f"{BASE_URL}/api/my-documents/visas/"
    headers = {
        'Authorization': f"Token {session.get('auth_token')}"
    }
    visas = []
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code == 200:
        visas=resp.json()
    else:
        for errors in resp.json().values():
            for error in errors:
                flash(error, 'danger')

    form = CreateVisaForm()

    if request.method == 'POST' and form.validate_on_submit():
        data = {
            'type': form.type.data,
            'entry_amount': form.entry_amount.data,
            'country': form.country.data
        }
        photo = form.photo.data
        files = {
            'photo': (photo.filename, photo.stream, photo.content_type)
        }
        create_resp = requests.post(url, data=data, files=files, headers=headers, timeout=10)
        if create_resp.status_code == 201:
            flash('Ваш запит на створення візи відправлено.', 'success')
            return redirect(url_for('get_visas'))
        else:
            for error in create_resp.json().values():
                flash(error, 'danger') 
    return render_template('get_visas.html', visas=visas, title="Візи", session=session, form=form)


@app.route('/my-visas/<int:pk>/extend/', methods=['GET', 'POST'])
@login_required
def extend_visa(pk):
    form = ExtendVisaForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            url = f"{BASE_URL}/api/my-documents/visas/{pk}/"
            data = {
                'reason': form.reason.data,
                'extension_date': form.extension_date.data
            }
            headers = {
                'Authorization': f"Token {session.get('auth_token')}"
            }
            resp = requests.patch(url, data=data, headers=headers, timeout=10)
            if resp.status_code == 200:
                flash('Ваш запит на подовження візи відправлено.', 'success')
                return redirect(url_for('get_visas'))
            else:
                for errors in resp.json().values():
                    flash(errors, 'danger')
    context = {
        'form': form,
        'title': "Заявка на подовження візи",
        'pk': pk,
        'session': session
    }
    return render_template('extend_visa.html', **context)


@app.route('/my-visas/<int:pk>/restore/', methods=['GET', 'POST'])
@login_required
def restore_visa(pk):
    form = RestoreVisaForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            url = f"{BASE_URL}/api/my-documents/visas/{pk}/"
            photo = form.photo.data
            files = {
                'photo': (photo.filename, photo.stream, photo.content_type)
            }
            headers = {
                'Authorization': f"Token {session.get('auth_token')}"
            }
            resp = requests.put(url, files=files, headers=headers, timeout=10)
            if resp.status_code == 200:
                flash('Ваш запит на відновлення візи через втрату надіслано.', 'success')
                return redirect(url_for('get_visas'))
            else:
                for errors in resp.json().values():
                    flash(errors, 'danger')
    context = {
        'form': form,
        'title': "Заявка на відновлення візи через втрату",
        'pk': pk,
        'session': session
    }
    return render_template('restore_visa.html', **context)


if __name__ == '__main__':
    app.run(debug=True)
