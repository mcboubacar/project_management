from app import create_app
from app.extensions import db
from app.models import User, Domain, Project, Task, ProjectHistory
from datetime import datetime, timedelta
import random

app = create_app()

def create_sample_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Create admin user
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)

        # Create project managers
        managers = []
        for i in range(1, 4):
            manager = User(
                username=f'manager{i}',
                email=f'manager{i}@example.com',
                role='manager'
            )
            manager.set_password(f'manager{i}123')
            managers.append(manager)
            db.session.add(manager)

        # Create monitor user
        monitor = User(username='monitor', email='monitor@example.com', role='monitor')
        monitor.set_password('monitor123')
        db.session.add(monitor)

        # Create domains
        domains = ['IT', 'Marketing', 'Finance', 'HR', 'Operations']
        domain_objects = []
        for domain in domains:
            d = Domain(name=domain, description=f'{domain} department projects')
            domain_objects.append(d)
            db.session.add(d)

        db.session.commit()

        # Create projects
        statuses = ['pending', 'in_progress', 'late', 'completed']
        today = datetime.utcnow().date()
        
        for i in range(1, 16):
            start_date = today - timedelta(days=random.randint(0, 30))
            end_date = start_date + timedelta(days=random.randint(10, 60))
            
            project = Project(
                title=f'Project {i}',
                description=f'Description for Project {i}',
                start_date=start_date,
                end_date=end_date,
                status=random.choice(statuses),
                domain_id=random.choice(domain_objects).id,
                manager_id=random.choice(managers).id
            )
            db.session.add(project)
            db.session.commit()

            # Create tasks for each project
            for j in range(1, random.randint(3, 8)):
                task_deadline = start_date + timedelta(days=random.randint(1, (end_date - start_date).days))
                task = Task(
                    title=f'Task {j} for Project {i}',
                    description=f'Description for Task {j}',
                    deadline=task_deadline,
                    status=random.choice(statuses),
                    project_id=project.id
                )
                db.session.add(task)
            
            # Update project progress
            project.update_progress()

            # Create project history
            for k in range(1, random.randint(3, 10)):
                history_date = start_date + timedelta(days=random.randint(0, (today - start_date).days if today > start_date else 0))
                history = ProjectHistory(
                    project_id=project.id,
                    progress=random.randint(0, 100),
                    status=random.choice(statuses),
                    recorded_at=history_date
                )
                db.session.add(history)

        db.session.commit()
        print("Sample data created successfully!")

if __name__ == '__main__':
    create_sample_data()