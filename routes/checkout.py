import json
from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models.course import Course, Progress
from models.purchase import Purchase
from models.notification import Notification
import requests

checkout_bp = Blueprint('checkout', __name__)


@checkout_bp.route('/<slug>')
@login_required
def checkout_page(slug):
    course = Course.query.filter_by(slug=slug, is_published=True).first_or_404()

    existing = Purchase.query.filter_by(
        user_id=current_user.id, course_id=course.id, status='completed'
    ).first()
    if existing:
        return redirect(url_for('courses.course_detail', slug=slug))

    gst = course.price * 0.18
    total = course.price + gst

    return render_template('public/checkout.html', course=course, gst=gst, total=total)


@checkout_bp.route('/initiate-payment', methods=['POST'])
@login_required
def initiate_payment():
    course_id = request.form.get('course_id', type=int)
    customer_name = request.form.get('customer_name', '').strip()
    customer_email = request.form.get('customer_email', '').strip()
    customer_phone = request.form.get('customer_phone', '').strip()
    profession = request.form.get('profession', '').strip()
    experience = request.form.get('experience', '').strip()

    course = db.session.get(Course, course_id)
    if not course or not course.is_published:
        return jsonify({'success': False, 'error': 'Invalid course'}), 400

    gst = course.price * 0.18
    total = course.price + gst

    razorpay_key = current_app.config.get('RAZORPAY_KEY_ID')
    razorpay_secret = current_app.config.get('RAZORPAY_SECRET')

    if not razorpay_key or not razorpay_secret:
        return jsonify({'success': False, 'error': 'Payment gateway not configured. Please try again later.'}), 503

    try:
        auth = (razorpay_key, razorpay_secret)
        data = {
            'amount': int(total * 100),
            'currency': 'INR',
            'receipt': f'course_{course.id}_user_{current_user.id}',
            'notes': {
                'user_id': str(current_user.id),
                'course_id': str(course.id),
                'customer_name': customer_name,
                'customer_email': customer_email,
            }
        }
        resp = requests.post('https://api.razorpay.com/v1/orders', json=data, auth=auth)
        if resp.status_code == 200:
            order = resp.json()
            purchase = Purchase(
                user_id=current_user.id,
                course_id=course.id,
                amount=total,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                profession=profession,
                experience=experience,
                payment_id=order['id'],
                status='pending'
            )
            db.session.add(purchase)
            db.session.commit()
            return jsonify({
                'success': True,
                'razorpay': True,
                'order_id': order['id'],
                'amount': order['amount'],
                'key': razorpay_key,
                'name': customer_name,
                'email': customer_email,
            })
        return jsonify({'success': False, 'error': 'Payment gateway error'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@checkout_bp.route('/verify-payment', methods=['POST'])
@login_required
def verify_payment():
    payment_id = request.form.get('razorpay_payment_id')
    order_id = request.form.get('razorpay_order_id')
    signature = request.form.get('razorpay_signature')

    purchase = Purchase.query.filter_by(payment_id=order_id, user_id=current_user.id).first()
    if not purchase:
        return jsonify({'success': False, 'error': 'Purchase not found'}), 404

    purchase.payment_id = payment_id
    purchase.status = 'completed'
    db.session.add(purchase)

    progress = Progress.query.filter_by(user_id=current_user.id, course_id=purchase.course_id).first()
    if not progress:
        progress = Progress(user_id=current_user.id, course_id=purchase.course_id)
        db.session.add(progress)

    notification = Notification(
        user_id=current_user.id,
        title='Payment Successful!',
        message=f'Your payment for "{purchase.course.title}" is confirmed. Happy learning!'
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({'success': True, 'redirect': url_for('courses.course_detail', slug=purchase.course.slug)})
