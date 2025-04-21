from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.forms.forms import DomainForm, ProjectForm, RegistrationForm, EditDomainForm
from app.models import Domain, Project, User
from app.extensions import db
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    projects = Project.query.all()
    users = User.query.all()
    domains = Domain.query.all()
    return render_template('admin/admin_dashboard.html', 
                         projects=projects, users=users, domains=domains)

@admin_bp.route('/create-user', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
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
    return render_template('admin/create_user.html', form=form)

@admin_bp.route('/manage-domains', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_domains():
    form = DomainForm()
    if form.validate_on_submit():
        domain = Domain(name=form.name.data, description=form.description.data)
        db.session.add(domain)
        db.session.commit()
        flash('New domain created!', 'success')
        return redirect(url_for('admin.manage_domains'))
    
    domains = Domain.query.all()
    return render_template('admin/manage_domains.html', form=form, domains=domains)

@admin_bp.route('/create-project', methods=['GET', 'POST'])
@login_required
@admin_required
def create_project():
    form = ProjectForm()
    form.domain.choices = [(d.id, d.name) for d in Domain.query.order_by('name')]
    form.manager.choices = [(u.id, u.username) for u in User.query.filter_by(role='manager').order_by('username')]
    
    if form.validate_on_submit():
        project = Project(
            title=form.title.data,
            description=form.description.data,
            domain_id=form.domain.data,
            manager_id=form.manager.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data
        )
        db.session.add(project)
        db.session.commit()
        flash('Project created successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('admin/create_project.html', form=form)

@admin_bp.route('/edit-domain/<int:domain_id>', methods=['POST'])
@login_required
@admin_required
def edit_domain(domain_id):
    domain = Domain.query.get_or_404(domain_id)
    new_name = request.form.get('name')
    new_description = request.form.get('description')
    
    if new_name:
        domain.name = new_name
    if new_description:
        domain.description = new_description
        
    db.session.commit()
    flash('Domaine mis à jour avec succès', 'success')
    return redirect(url_for('admin.manage_domains'))

@admin_bp.route('/delete-domain/<int:domain_id>')
@login_required
@admin_required
def delete_domain(domain_id):
    domain = Domain.query.get_or_404(domain_id)
    
    if domain.projects.count() > 0:
        flash('Impossible de supprimer un domaine avec des projets associés', 'danger')
    else:
        db.session.delete(domain)
        db.session.commit()
        flash('Domaine supprimé avec succès', 'success')
    
    return redirect(url_for('admin.manage_domains'))