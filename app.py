import os
import secrets
import requests

from flask import Flask, request, render_template, url_for, redirect, session, flash

from administration import admin_app
from authentication import auth_app
from forms import ExtendVisaForm, RestoreVisaForm, CreateVisaForm
from permissions import login_required
from utils import STATUS_CHOICES, TASK_TITLES


app = Flask(__name__)
app.register_blueprint(auth_app, url_prefix='/auth')
app.register_blueprint(admin_app, url_prefix='/admin')
app.config['SECRET_KEY'] = secrets.token_hex(16)

BASE_URL = os.environ.get("BASE_URL")


@app.route('/')
@app.route('/home/')
def home():
    return render_template('home.html', title="Головна сторінка", session=session)

                
@app.route('/my-visas/', methods=['GET', 'POST'])
@login_required(role='user')
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
@login_required(role='user')
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
@login_required(role='user')
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


@app.route('/my-requests/')
@login_required(role='user')
def get_requests():
    url = f"{BASE_URL}/api/my-documents/tasks/?page=all&title=visa"
    headers = {
        'Authorization': f"Token {session.get('auth_token')}"
    }
    tasks = []
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code == 200:
        tasks = resp.json()['tasks']
    else:
        for errors in resp.json().values():
            for error in errors:
                flash(error, 'danger')

    return render_template('get_tasks.html', tasks=tasks, title="Ваші заявки", session=session, TASK_TITLES=dict(TASK_TITLES), STATUS_CHOICES=STATUS_CHOICES)


if __name__ == '__main__':
    app.run(debug=True)
