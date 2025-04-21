from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import or_
from app.forms import TaskForm, UpdateTaskStatusForm, ProjectForm
from app.models import Project, Task, ProjectHistory, Domain
from app.extensions import db
from app.utils.decorators import manager_required

project_bp = Blueprint('project', __name__, url_prefix='/project')

@project_bp.route('/dashboard')
@login_required
@manager_required
def dashboard():

    projects = Project.query.filter_by(manager_id=current_user.id).all()
    print("Entry point for peoject.dashboard")
    # Calculate statistics
    stats = {
        'total': len(projects),
        'pending': len([p for p in projects if p.status == 'pending']),
        'in_progress': len([p for p in projects if p.status == 'in_progress']),
        'late': len([p for p in projects if p.status == 'late']),
        'completed': len([p for p in projects if p.status == 'completed'])
    }
    print("after calculate stats")
    return render_template('project_manager/dashboard.html', projects=projects, stats=stats)

@project_bp.route('/project/<int:project_id>')
@login_required
@manager_required
def project_detail(project_id):

    project = Project.query.get_or_404(project_id)
    if project.manager_id != current_user.id and not current_user.is_admin():
        flash("In test",'danger')
        flash('You are not authorized to view this project.', 'danger')
        return redirect(url_for('project.dashboard'))
    
    tasks = project.tasks.order_by(Task.deadline).all()
    form = TaskForm()
    status_form = UpdateTaskStatusForm()
    
    return render_template('project_manager/project_detail.html', 
                         project=project, tasks=tasks, form=form, status_form=status_form)


@project_bp.route('/create-task/<int:project_id>', methods=['GET','POST'])
@login_required
@manager_required
def create_task(project_id):

    project = Project.query.get_or_404(project_id)
    if project.manager_id != current_user.id and not current_user.is_admin():
        flash('You are not authorized to add tasks to this project.', 'danger')
        return redirect(url_for('project.dashboard'))
    
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            deadline=form.deadline.data,
            project_id=project_id
        )
        db.session.add(task)
        db.session.commit()
        
        # Update project progress and status
        project.update_progress()
        
        # Record history
        history = ProjectHistory(
            project_id=project_id,
            progress=project.progress,
            status=project.status
        )
        db.session.add(history)
        db.session.commit()
        
        flash('Task added successfully!', 'success')
        return redirect(url_for('project.dashboard'))
    
    # return redirect(url_for('project.project_detail', project_id=project_id))
    return render_template('project_manager/create_task.html',project=project,form=form)
                        #  project=project, tasks=tasks, form=form, status_form=status_form)

@project_bp.route('/update-task-status/<int:task_id>', methods=['GET','POST'])
@login_required
@manager_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    project = Project.query.get_or_404(task.project_id)
    
    if project.manager_id != current_user.id and not current_user.is_admin():
        flash('You are not authorized to update this task.', 'danger')
        return redirect(url_for('project.dashboard'))
    
    form = UpdateTaskStatusForm()
    if form.validate_on_submit():
        task.status = form.status.data
        db.session.commit()
        
        # Update project progress and status
        project.update_progress()
        
        # Record history
        history = ProjectHistory(
            project_id=project.id,
            progress=project.progress,
            status=project.status
        )
        db.session.add(history)
        db.session.commit()
        
        flash('Task status updated!', 'success')
        return redirect(url_for('project.dashboard'))

    return redirect(url_for('project.project_detail', project_id=project.id))

@project_bp.route('/create-project', methods=['GET', 'POST'])
@login_required
@manager_required
def create_project():

    form = ProjectForm()
    form.domain.choices = [(d.id, d.name) for d in Domain.query.order_by('name')]
    
    # Si l'utilisateur est admin, il peut choisir le manager
    if current_user.is_admin():
        form.manager.choices = [(u.id, u.username) for u in User.query.filter_by(role='manager').order_by('username')]
    else:
        # Pour les managers normaux, le manager est automatiquement l'utilisateur courant
        form.manager.data = current_user.id
        del form.manager  # On supprime le champ pour les non-admins

    if form.validate_on_submit():
        project = Project(
            title=form.title.data,
            description=form.description.data,
            domain_id=form.domain.data,
            manager_id=current_user.id if not current_user.is_admin() else form.manager.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data
        )
        db.session.add(project)
        db.session.commit()
        
        flash('Projet créé avec succès!', 'success')
        return redirect(url_for('project.dashboard'))
    
    return render_template('project_manager/create_project.html', form=form)