import datetime
from extensions import db


class Purchase(db.Model):
    __tablename__ = 'purchases'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    amount = db.Column(db.Float, default=0.0)
    customer_name = db.Column(db.String(100), nullable=True)
    customer_email = db.Column(db.String(120), nullable=True)
    customer_phone = db.Column(db.String(20), nullable=True)
    profession = db.Column(db.String(100), nullable=True)
    experience = db.Column(db.String(50), nullable=True)
    payment_id = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default='pending')
    purchased_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'amount': self.amount,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'profession': self.profession,
            'experience': self.experience,
            'payment_id': self.payment_id,
            'status': self.status,
            'purchased_at': self.purchased_at.isoformat() if self.purchased_at else None,
        }

    def __repr__(self):
        return f'<Purchase {self.id} - {self.status}>'
