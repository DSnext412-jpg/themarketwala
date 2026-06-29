import datetime
from extensions import db


class Blog(db.Model):
    __tablename__ = 'blogs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=True)
    featured_image = db.Column(db.String(500), nullable=True)
    excerpt = db.Column(db.Text, nullable=True)
    seo_title = db.Column(db.String(200), nullable=True)
    seo_description = db.Column(db.String(300), nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'featured_image': self.featured_image,
            'excerpt': self.excerpt,
            'seo_title': self.seo_title,
            'seo_description': self.seo_description,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Blog {self.title}>'
