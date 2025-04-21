from flask import Blueprint, render_template, make_response, flash
from flask_login import login_required, current_user
from app.models import Project, User, Domain, Task, ProjectHistory
from app.utils.decorators import admin_required, manager_required, monitor_required
from app.utils.report_generator import generate_pdf_report
from datetime import datetime
from app.extensions import db
from weasyprint import HTML
import tempfile

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/project-report/<int:project_id>')
@login_required
@manager_required
def project_report(project_id):
    # Get project with joined data
    project = db.session.query(Project).join(Domain).join(User).options(
        db.contains_eager(Project.domain),
        db.contains_eager(Project.manager)
    ).filter(
        Project.id == project_id,
        Project.manager_id == current_user.id
    ).first_or_404()

    # Get tasks ordered by deadline
    tasks = Task.query.filter_by(project_id=project_id).order_by(Task.deadline).all()

    # Format tasks for display
    formatted_tasks = [{
        'title': t.title,
        'deadline': t.deadline.strftime('%Y-%m-%d'),
        'status': t.status.replace('_', ' ').title()
    } for t in tasks]

    # Get history
    history = ProjectHistory.query.filter_by(project_id=project_id).order_by(
        ProjectHistory.recorded_at.desc()).limit(10).all()

    # Format history
    formatted_history = [{
        'recorded_at': h.recorded_at.strftime('%Y-%m-%d %H:%M'),
        'status': h.status.replace('_', ' ').title(),
        'progress': f"{h.progress}%"
    } for h in history]

    # Generate PDF
    pdf = generate_pdf_report(
        template='project_report.html',
        project={
            'title': project.title,
            'domain': project.domain.name,
            'manager': project.manager.username,
            'start_date': project.start_date.strftime('%Y-%m-%d'),
            'end_date': project.end_date.strftime('%Y-%m-%d'),
            'status': project.status.replace('_', ' ').title(),
            'progress': f"{project.progress}%",
            'description': project.description or "Aucune description"
        },
        tasks=formatted_tasks,
        history=formatted_history,
        current_date=datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    )
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=project_{project_id}_report.pdf'
    return response

@reports_bp.route('/global-report')
@login_required
@monitor_required
def global_report():
    # Récupérer les mêmes données que pour le tableau de bord
    domains = Domain.query.all()
    managers = User.query.filter_by(role='manager').all()
    projects = Project.query.all()
    
    # Calculer les statistiques comme dans le tableau de bord
    stats = {
        'completed': sum(1 for p in projects if p.status == 'completed'),
        'in_progress': sum(1 for p in projects if p.status == 'in_progress'),
        'late': sum(1 for p in projects if p.status == 'late'),
        'pending': sum(1 for p in projects if p.status == 'pending'),
        'total': len(projects)
    }
    
    # Calculer les stats par domaine et manager comme dans le tableau de bord
    domain_manager_stats = []
    for domain in domains:
        domain_projects = [p for p in projects if p.domain_id == domain.id]
        domain_stats = {
            'name': domain.name,
            'completed': sum(1 for p in domain_projects if p.status == 'completed'),
            'in_progress': sum(1 for p in domain_projects if p.status == 'in_progress'),
            'late': sum(1 for p in domain_projects if p.status == 'late'),
            'total': len(domain_projects),
            'managers': []
        }
        
        for manager in managers:
            manager_projects = [p for p in domain_projects if p.manager_id == manager.id]
            if manager_projects:
                domain_stats['managers'].append({
                    'name': manager.username,
                    'completed': sum(1 for p in manager_projects if p.status == 'completed'),
                    'in_progress': sum(1 for p in manager_projects if p.status == 'in_progress'),
                    'late': sum(1 for p in manager_projects if p.status == 'late'),
                    'total': len(manager_projects)
                })
        
        domain_manager_stats.append(domain_stats)
    
    # Générer le HTML avec le template PDF
    html = render_template(
        'reports/global_pdf.html',
        domains=domains,
        managers=managers,
        projects=projects,
        stats=stats,
        domain_manager_stats=domain_manager_stats,
        current_date=datetime.now()  # Ajout de la date courante
    )
    
    # Créer un PDF avec WeasyPrint
    pdf = HTML(string=html).write_pdf()
    
    # Créer la réponse
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=rapport_global.pdf'
    
    return response

@reports_bp.route('/manager-global-report')
@login_required
@manager_required
def manager_global_report():
    # Get projects with joined data to avoid N+1 queries
    projects = db.session.query(Project).join(Domain).filter(
        Project.manager_id == current_user.id
    ).options(db.contains_eager(Project.domain)).all()

    # Récupération des projets avec jointure pour éviter le problème N+1
    projects = db.session.query(Project).join(Domain).filter(
        Project.manager_id == current_user.id
    ).options(db.contains_eager(Project.domain)).all()

    # Calcul des statistiques par domaine avec la progression moyenne
    domain_stats = []
    for domain in Domain.query.all():
        domain_projects = [p for p in projects if p.domain_id == domain.id]
        if not domain_projects:
            continue
            
        total_projects = len(domain_projects)
        completed_projects = sum(1 for p in domain_projects if p.status == 'completed')
        
        # Calcul de la progression MOYENNE des projets du domaine
        avg_progress = sum(p.progress for p in domain_projects) / total_projects
        
        domain_stats.append({
            'domain': domain,
            'total': total_projects,
            'completed': completed_projects,
            'progress': round(avg_progress, 1)  # Arrondi à 1 décimale
        })

    # Get history with project titles
    history = db.session.query(ProjectHistory).join(Project).filter(
        Project.manager_id == current_user.id
    ).order_by(ProjectHistory.recorded_at.desc()).limit(10).all()

    # Format dates properly before passing to template
    formatted_history = [{
        'project_title': h.project.title,
        'status': h.status.replace('_', ' ').title(),
        'progress': f"{h.progress}%",
        'recorded_at': h.recorded_at.strftime('%Y-%m-%d %H:%M')
    } for h in history]

    formatted_projects = [{
        'title': p.title,
        'domain_name': p.domain.name,
        'end_date': p.end_date.strftime('%Y-%m-%d'),
        'status': p.status.replace('_', ' ').title(),
        'progress': f"{p.progress}%"
    } for p in projects]

    # Generate PDF with properly formatted data
    pdf = generate_pdf_report(
        template='manager_global_report.html',
        stats=stats,
        domain_stats=domain_stats,
        history=formatted_history,
        projects=formatted_projects,
        current_date=datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    )
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=manager_global_report.pdf'
    return response