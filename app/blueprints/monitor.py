from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Project, Domain, User
from app.utils.decorators import monitor_required
from app.extensions import db

monitor_bp = Blueprint('monitor', __name__, url_prefix='/monitor')

@monitor_bp.route('/global-dashboard')
@login_required
@monitor_required
def global_dashboard():
    projects = Project.query.all()
    domains = Domain.query.all()
    
    # Calcul des statistiques globales
    stats = {
        'total': Project.query.count(),
        'completed': Project.query.filter_by(status='completed').count(),
        'in_progress': Project.query.filter_by(status='in_progress').count(),
        'late': Project.query.filter_by(status='late').count(),
        'pending': Project.query.filter_by(status='pending').count()
    }

    # Statistiques par domaine
    domains = []
    for domain in Domain.query.all():
        projects = Project.query.filter_by(domain_id=domain.id).all()
        domains.append({
            'name': domain.name,
            'total': len(projects),
            'completed': len([p for p in projects if p.status == 'completed']),
            'in_progress': len([p for p in projects if p.status == 'in_progress']),
            'late': len([p for p in projects if p.status == 'late']),
            'pending': len([p for p in projects if p.status == 'pending'])
        })

    # Statistiques par manager
    managers = []
    for manager in User.query.filter_by(role='manager').all():
        projects = Project.query.filter_by(manager_id=manager.id).all()
        managers.append({
            'name': manager.username,
            'total': len(projects),
            'completed': len([p for p in projects if p.status == 'completed']),
            'in_progress': len([p for p in projects if p.status == 'in_progress']),
            'late': len([p for p in projects if p.status == 'late']),
            'pending': len([p for p in projects if p.status == 'pending'])
        })

    # Statistiques combinées domaines/managers
    domain_manager_stats = []
    for domain in Domain.query.all():
        domain_projects = Project.query.filter_by(domain_id=domain.id).all()
        managers_data = []
        
        # Trouver tous les managers concernés par ce domaine
        managers_set = {p.manager for p in domain_projects}
        
        for manager in managers_set:
            manager_projects = [p for p in domain_projects if p.manager_id == manager.id]
            managers_data.append({
                'name': manager.username,
                'completed': len([p for p in manager_projects if p.status == 'completed']),
                'in_progress': len([p for p in manager_projects if p.status == 'in_progress']),
                'late': len([p for p in manager_projects if p.status == 'late']),
                'pending': len([p for p in manager_projects if p.status == 'pending']),
                'total': len(manager_projects)
            })
        
        domain_manager_stats.append({
            'name': domain.name,
            'completed': len([p for p in domain_projects if p.status == 'completed']),
            'in_progress': len([p for p in domain_projects if p.status == 'in_progress']),
            'late': len([p for p in domain_projects if p.status == 'late']),
            'pending': len([p for p in domain_projects if p.status == 'pending']),
            'total': len(domain_projects),
            'managers': sorted(managers_data, key=lambda x: x['name'])
        })

    # Trier les domaines par nom
    domain_manager_stats = sorted(domain_manager_stats, key=lambda x: x['name'])
    managers = sorted(managers, key=lambda x: x['name'])
    domains = sorted(domains, key=lambda x: x['name'])

    # Récupérer tous les projets pour le tableau détaillé
    projects = Project.query.options(
        db.joinedload(Project.manager),
        db.joinedload(Project.domain)
    ).order_by(
        Project.manager_id,
        Project.domain_id,
        Project.status
    ).all()

    return render_template('monitor/global_dashboard.html',
                        domain_manager_stats=domain_manager_stats,
                        domains=domains,
                        managers=managers,
                        stats=stats,
                        projects=projects)