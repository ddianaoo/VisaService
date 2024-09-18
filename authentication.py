import os
import requests
from flask import Blueprint, request, render_template, url_for, redirect, session, flash
from forms import SignUpForm, LoginForm
from permissions import login_required


BASE_URL = os.environ.get("BASE_URL")
auth_app = Blueprint('auth', __name__, template_folder='templates/authentication')


@auth_app.route('/signup/', methods=['GET', 'POST'])
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

    return render_template('signup_page.html', form=form, title="Реєстрація", session=session)


@auth_app.route('/login/', methods=['GET', 'POST'])
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
                url = f"{BASE_URL}/api/auth/users/me"
                headers = {
                    'Authorization': f"Token {auth_token}"
                }
                user = requests.get(url, headers=headers, timeout=10).json()
                session['user'] = user
                flash('Ви успішно увійшли в обліковий запис.', 'success')
                return redirect(url_for('home'))
            else:
                for errors in resp.json().values():
                    for error in errors:
                        flash(error, 'danger')

    return render_template('login_page.html', form=form, title="Вхід", session=session)


@auth_app.route('/logout/')
@login_required()
def logout():
    if session.get('auth_token') and session.get('user'):
        session.pop('auth_token', None)
        session.pop('user', None)
        flash('Ви вийшли з облікового запису.', 'success')
    return redirect(url_for('home'))
