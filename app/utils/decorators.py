from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

# def logout_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if current_user.is_authenticated:
#             flash('You are already logged in.', 'info')
#             if current_user.is_manager():
#                 return redirect(url_for('project.dashboard'))
#             elif current_user.is_monitor():
#                 return redirect(url_for('monitor.global_dashboard'))
#             else:
#                 return redirect(url_for('admin.admin_dashboard'))
#         return f(*args, **kwargs)
#     return decorated_function

def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash('Vous êtes déjà connecté.', 'info')
            if current_user.role == 'manager':
                return redirect(url_for('project.dashboard'))
            elif current_user.role == 'monitor':
                return redirect(url_for('monitor.global_dashboard'))
            elif current_user.role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_manager():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def monitor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_monitor():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function