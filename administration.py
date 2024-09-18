import os
import requests
from flask import Blueprint, request, render_template, url_for, redirect, session, flash
from permissions import login_required
from forms import ComleteTaskForm
from utils import STATUS_CHOICES, TASK_TITLES, COUNTRY_CHOICES, ENTRY_CHOICES, TYPE_CHOICES, GENDER_CHOICES


BASE_URL = os.environ.get("BASE_URL")
admin_app = Blueprint('admin', __name__, template_folder='templates/administration')


def fetch_task(pk):
    url = f"{BASE_URL}/api/staff/tasks/{pk}"
    headers = {'Authorization': f"Token {session.get('auth_token')}"}
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        task = resp.json()
        task['title'] = dict(TASK_TITLES).get(task['title'], task['title'])
        task['status_display'] = STATUS_CHOICES.get(task['status'], 'Unknown')
        task['user']['nationality'] = dict(COUNTRY_CHOICES).get(task['user']['nationality'], 'Unknown')
        task['user']['sex'] = dict(GENDER_CHOICES).get(task['user']['sex'], 'Unknown')
        if task['title'] == 'Створення візи':
            task['user_data']['visa_country'] = dict(COUNTRY_CHOICES).get(task['user_data']['visa_country'], 'Unknown')
            task['user_data']['visa_type'] = dict(TYPE_CHOICES).get(task['user_data']['visa_type'], 'Unknown')
            task['user_data']['visa_entry_amount'] = dict(ENTRY_CHOICES).get(task['user_data']['visa_entry_amount'], 'Unknown')
        return task
    else:
        flash("Помилка: даної заяви не знайдено.", 'danger') 
    return None


@admin_app.route('/tasks/')
@login_required(role='staff')
def get_tasks():
    url = f"{BASE_URL}/api/staff/tasks/?page=all&title=visa"
    headers = {
        'Authorization': f"Token {session.get('auth_token')}"
    }
    tasks = []
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        tasks = resp.json()['tasks']
    else:
        for errors in resp.json().values():
            for error in errors:
                flash(error, 'danger')
    context = {
        'tasks': tasks,
        'title': 'Журнал заяв',
        'session': session,
        'TASK_TITLES': dict(TASK_TITLES),
        'STATUS_CHOICES': STATUS_CHOICES
    }
    return render_template('get_admin_tasks.html', **context)


@admin_app.route('/tasks/<int:pk>', methods=['GET'])
@login_required(role='staff')
def get_task_by_pk(pk): 
    task = fetch_task(pk)
    if not task:
        return redirect(url_for('admin.get_tasks'))
    form = ComleteTaskForm()
    return render_template('get_task_by_pk.html', task=task, form=form, session=session)


@admin_app.route('/tasks/<int:pk>/create/', methods=['GET', 'POST'])
@login_required(role='staff')
def create_task_staff(pk):
    task = fetch_task(pk)
    if not task:
        return redirect(url_for('admin.get_tasks'))
    
    form = ComleteTaskForm()
    if request.method == 'POST' and form.validate_on_submit():
        data = {
            'place_of_issue': form.place_of_issue.data,
            'date_of_issue': form.date_of_issue.data,
            'date_of_expiry': form.date_of_expiry.data
        }
        headers = {'Authorization': f"Token {session.get('auth_token')}"}
        resp = requests.post(f"{BASE_URL}/api/staff/create-visa/{pk}/", data=data, headers=headers)
        if resp.status_code == 201:
            flash(f"Заявка №{pk}: Створення візи опрацьовано.", 'success')
            return redirect(url_for('admin.get_tasks'))
        else:
            for error in resp.json().values():
                flash(error, 'danger') 

    return render_template('get_task_by_pk.html', task=task, form=form, session=session)


@admin_app.route('/tasks/<int:pk>/restore/', methods=['GET', 'POST'])
@login_required(role='staff')
def restore_task_staff(pk):
    task = fetch_task(pk)
    if not task:
        return redirect(url_for('admin.get_tasks'))

    form = ComleteTaskForm()
    if request.method == 'POST' and form.validate_on_submit():
        data = {
            'place_of_issue': form.place_of_issue.data,
            'date_of_issue': form.date_of_issue.data,
            'date_of_expiry': form.date_of_expiry.data
        }
        headers = {'Authorization': f"Token {session.get('auth_token')}"}
        resp = requests.put(f"{BASE_URL}/api/staff/restore-visa/{pk}/", data=data, headers=headers)
        if resp.status_code == 201:
            flash(f"Заявка №{pk}: Створення візи опрацьовано.", 'success')
            return redirect(url_for('admin.get_tasks'))
        else:
            for error in resp.json().values():
                flash(error, 'danger') 

    return render_template('get_task_by_pk.html', task=task, form=form, session=session)


@admin_app.route('/tasks/<int:pk>/extend/')
@login_required(role='staff')
def extend_task_staff(pk):
    url = f"{BASE_URL}/api/staff/extend-visa/{pk}/"
    headers = {
        'Authorization': f"Token {session.get('auth_token')}"
    }
    resp = requests.patch(url, headers=headers)
    if resp.status_code == 200:
        flash(f"Заявка №{pk}: Подовження візи опрацьовано.", 'success')
    else:
        for errors in resp.json().values():
            for error in errors:
                flash(error, 'danger')
                
    return redirect(url_for('admin.get_task_by_pk', pk=pk))


@admin_app.route('/tasks/<int:pk>/reject/')
@login_required(role='staff')
def reject_task_staff(pk):
    url = f"{BASE_URL}/api/staff/reject-task/{pk}/"
    headers = {
        'Authorization': f"Token {session.get('auth_token')}"
    }
    resp = requests.patch(url, headers=headers)
    if resp.status_code == 200:
        flash(f"Заявку №{pk} було відхилено.", 'success')
    else:
        for errors in resp.json().values():
            for error in errors:
                flash(error, 'danger')
                
    return redirect(url_for('admin.get_task_by_pk', pk=pk))
