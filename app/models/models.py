from datetime import datetime
from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, manager, monitor
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    projects = db.relationship('Project', backref='manager', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_manager(self):
        return self.role == 'manager'
    
    def is_monitor(self):
        return self.role == 'monitor'

class Domain(db.Model):
    __tablename__ = 'domains'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    projects = db.relationship('Project', backref='domain', lazy='dynamic')

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, late, completed
    progress = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    domain_id = db.Column(db.Integer, db.ForeignKey('domains.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    tasks = db.relationship('Task', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def update_progress(self):
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            self.progress = 0
        else:
            completed_tasks = self.tasks.filter_by(status='completed').count()
            self.progress = int((completed_tasks / total_tasks) * 100)
        
        # Update project status based on progress and dates
        today = datetime.utcnow().date()
        if self.progress == 100:
            self.status = 'completed'
        elif self.progress > 0:
            if self.end_date < today:
                self.status = 'late'
            else:
                self.status = 'in_progress'
        else:
            if self.start_date > today:
                self.status = 'pending'
            elif self.end_date < today:
                self.status = 'late'
            else:
                self.status = 'in_progress'
        
        db.session.commit()

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, late, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    def update_status(self):
        today = datetime.utcnow().date()
        if self.status != 'completed':
            if self.deadline < today:
                self.status = 'late'
            elif self.status == 'pending' and self.deadline >= today:
                self.status = 'in_progress'
        db.session.commit()

class ProjectHistory(db.Model):
    __tablename__ = 'project_history'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    progress = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    project = db.relationship('Project', backref='history', lazy=True)