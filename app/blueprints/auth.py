from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from app.forms import LoginForm, RegistrationForm, ChangePasswordForm
from app.models import User
from app.extensions import db
from app.utils.decorators import logout_required, admin_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
@logout_required
def login():
    # Si l'utilisateur est déjà authentifié, on le redirige
    if current_user.is_authenticated:
        if current_user.role == 'manager':
            return redirect(url_for('project.dashboard'))
        elif current_user.role == 'monitor':
            return redirect(url_for('monitor.global_dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
    form = LoginForm()
    print("Entry of login")
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            session['role'] = user.role
            print(f"role: ,<{user.role}>")
            next_page = request.args.get('next')
            print(f"next page:  <{next_page}>")
            flash('You have been logged in successfully!', 'success')
            if current_user.is_manager():
                dashboard='project.dashboard'
            elif current_user.is_monitor():
                dashboard='monitor.global_dashboard'
            else:
                dashboard='admin.admin_dashboard'

            print(f"Selected dashboard: <{dashboard}>")
            return redirect(url_for(dashboard))
            
        else:
            flash('Invalid username or password', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
@admin_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'New {form.role.data} account created for {form.username.data}!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@logout_required
def change_password():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if not user:
            flash('Nom d\'utilisateur incorrect', 'danger')
            return redirect(url_for('auth.change_password'))
            
        if not user.check_password(form.current_password.data):
            flash('Mot de passe actuel incorrect', 'danger')
            return redirect(url_for('auth.change_password'))
            
        try:
            user.set_password(form.new_password.data)
            db.session.commit()
            flash('Mot de passe changé avec succès! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Une erreur est survenue: ' + str(e), 'danger')
    
    return render_template('auth/change_password.html', form=form)