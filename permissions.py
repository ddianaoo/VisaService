from functools import wraps
from flask import url_for, redirect, session, flash


def is_authenticated():
    """Checking for the presence of an authentication token in the session."""
    return session.get('auth_token') is not None


def is_staff():
    """Checking for admin permissions."""
    return session.get('user', {}).get('is_staff', False)


def login_required(role='authenticated_user'):
    """A decorator for checking user permissions based on role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_authenticated():
                flash('Ви ще не увійшли в акаунт.', 'danger')
                return redirect(url_for('auth.login'))
            
            if role == 'staff':
                if is_staff():
                    return f(*args, **kwargs)
                flash('У вас нема таких прав.', 'danger')
                return redirect(url_for('home'))
            
            if role == 'user':
                if not is_staff():
                    return f(*args, **kwargs)
                flash('Ви увійшли у систему з акаунту працівника.', 'danger')
                return redirect(url_for('home'))  
            
            if role is 'authenticated_user':
                return f(*args, **kwargs)

        return decorated_function
    return decorator
