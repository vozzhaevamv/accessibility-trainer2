from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
import json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    level = db.Column(db.String(20), default='beginner')
    progress = db.relationship('UserProgress', backref='user', lazy=True)
    metrics = db.relationship('UserMetric', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    question = db.Column(db.String(200), nullable=False)
    code_snippet = db.Column(db.Text)
    correct_answer = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20))
    task_type = db.Column(db.String(20))  # 'code' или 'quiz'
    progresses = db.relationship('UserProgress', backref='task', lazy=True)
    metrics = db.relationship('UserMetric', backref='task', lazy=True)

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    correct_attempts = db.Column(db.Integer, default=0)
    last_attempt = db.Column(db.DateTime)

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    options = db.Column(db.Text)  # JSON строка с вариантами
    correct_answer = db.Column(db.String(1), nullable=False)  # буква правильного ответа
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    
    def get_options(self):
        """Возвращает варианты ответов в виде словаря"""
        if self.options:
            return json.loads(self.options)
        return {}

class UserMetric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    time_spent = db.Column(db.Integer)  # в секундах
    success = db.Column(db.Boolean)

    def complete_task(self, success):
        self.end_time = datetime.utcnow()
        self.time_spent = (self.end_time - self.start_time).total_seconds()
        self.success = success
        db.session.commit()