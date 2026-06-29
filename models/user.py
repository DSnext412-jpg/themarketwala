import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    supabase_uid = db.Column(db.String(255), unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    role = db.Column(db.String(20), default='student')
    avatar_url = db.Column(db.String(500), nullable=True)
    experience_level = db.Column(db.String(50), default='beginner')
    interests = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    purchases = db.relationship('Purchase', backref='user', lazy='dynamic')
    bookmarks = db.relationship('Bookmark', backref='user', lazy='dynamic')
    progress = db.relationship('Progress', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def total_courses_purchased(self):
        return self.purchases.filter_by(status='completed').count()

    def total_completed_courses(self):
        from models.course import Course, Progress
        return Progress.query.join(Course).filter(
            Progress.user_id == self.id,
            Progress.completed == True
        ).count()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'avatar_url': self.avatar_url,
            'experience_level': self.experience_level,
            'interests': self.interests,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<User {self.name} ({self.role})>'
