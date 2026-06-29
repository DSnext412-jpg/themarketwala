import datetime
from extensions import db


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    thumbnail = db.Column(db.String(500), nullable=True)
    content = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    difficulty = db.Column(db.String(50), default='beginner')
    price = db.Column(db.Float, default=0.0)
    reading_time = db.Column(db.String(50), nullable=True)
    lecture_times = db.Column(db.Text, nullable=True)
    drive_link = db.Column(db.String(500), nullable=True)
    live_meeting_link = db.Column(db.String(500), nullable=True)
    tags = db.Column(db.String(500), nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    purchases = db.relationship('Purchase', backref='course', lazy='dynamic')
    bookmarks = db.relationship('Bookmark', backref='course', lazy='dynamic')
    progress = db.relationship('Progress', backref='course', lazy='dynamic')

    def tag_list(self):
        if self.tags:
            return [t.strip() for t in self.tags.split(',')]
        return []

    def lecture_list(self):
        if self.lecture_times:
            return [l.strip() for l in self.lecture_times.split('\n') if l.strip()]
        return []

    def purchase_count(self):
        return self.purchases.filter_by(status='completed').count()

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'thumbnail': self.thumbnail,
            'category': self.category,
            'difficulty': self.difficulty,
            'price': self.price,
            'reading_time': self.reading_time,
            'tags': self.tag_list(),
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Course {self.title}>'


class Bookmark(db.Model):
    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'course_id'),)

    def __repr__(self):
        return f'<Bookmark user={self.user_id} course={self.course_id}>'


class Progress(db.Model):
    __tablename__ = 'progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    completion_percentage = db.Column(db.Float, default=0.0)
    completed = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'course_id'),)

    def __repr__(self):
        return f'<Progress user={self.user_id} course={self.course_id} {self.completion_percentage}%>'
