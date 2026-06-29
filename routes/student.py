import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.course import Course, Bookmark, Progress
from models.purchase import Purchase
from models.notification import Notification
from models.user import User

student_bp = Blueprint('student', __name__)


@student_bp.before_request
def require_login():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))


@student_bp.route('/')
def overview():
    purchases = Purchase.query.filter_by(user_id=current_user.id, status='completed').all()
    purchased_course_ids = [p.course_id for p in purchases]

    recent_purchases = Purchase.query.filter_by(
        user_id=current_user.id, status='completed'
    ).order_by(Purchase.purchased_at.desc()).limit(5).all()

    notifications = Notification.query.filter_by(user_id=current_user.id, read=False).order_by(
        Notification.created_at.desc()).limit(5).all()

    progress_data = Progress.query.filter(
        Progress.user_id == current_user.id,
        Progress.course_id.in_(purchased_course_ids) if purchased_course_ids else False
    ).all() if purchased_course_ids else []

    return render_template('student/overview.html',
                           purchases=purchases,
                           recent_purchases=recent_purchases,
                           notifications=notifications,
                           progress_data=progress_data)


@student_bp.route('/progress')
def learning_progress():
    purchases = Purchase.query.filter_by(user_id=current_user.id, status='completed').all()
    purchased_course_ids = [p.course_id for p in purchases]
    courses = Course.query.filter(Course.id.in_(purchased_course_ids)).all() if purchased_course_ids else []
    progress_data = {p.course_id: p for p in Progress.query.filter_by(user_id=current_user.id).all()}
    return render_template('student/progress.html', courses=courses, progress_data=progress_data)


@student_bp.route('/progress/update', methods=['POST'])
def update_progress():
    course_id = request.form.get('course_id', type=int)
    percentage = request.form.get('percentage', type=float)

    progress = Progress.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    if not progress:
        progress = Progress(user_id=current_user.id, course_id=course_id)
        db.session.add(progress)

    progress.completion_percentage = min(percentage, 100)
    progress.completed = percentage >= 100
    db.session.commit()

    return jsonify({'success': True, 'completed': progress.completed})


@student_bp.route('/bookmarks')
def bookmarks():
    bookmark_records = Bookmark.query.filter_by(user_id=current_user.id).all()
    course_ids = [b.course_id for b in bookmark_records]
    courses = Course.query.filter(Course.id.in_(course_ids)).all() if course_ids else []
    return render_template('student/bookmarks.html', courses=courses)


@student_bp.route('/bookmark/toggle', methods=['POST'])
def toggle_bookmark():
    course_id = request.form.get('course_id', type=int)
    bookmark = Bookmark.query.filter_by(user_id=current_user.id, course_id=course_id).first()

    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
        return jsonify({'success': True, 'bookmarked': False})
    else:
        bookmark = Bookmark(user_id=current_user.id, course_id=course_id)
        db.session.add(bookmark)
        db.session.commit()
        return jsonify({'success': True, 'bookmarked': True})


@student_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name)
        current_user.experience_level = request.form.get('experience_level', current_user.experience_level)
        current_user.interests = request.form.get('interests', current_user.interests)
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student.profile'))
    return render_template('student/profile.html')


@student_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if current_password and new_password:
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'error')
                return render_template('student/settings.html')

            if new_password != confirm_password:
                flash('New passwords do not match.', 'error')
                return render_template('student/settings.html')

            current_user.set_password(new_password)
            db.session.commit()
            flash('Password updated successfully!', 'success')

    return render_template('student/settings.html')


@student_bp.route('/notifications')
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()).all()
    return render_template('student/notifications.html', notifications=notifications)


@student_bp.route('/notifications/read', methods=['POST'])
def mark_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, read=False).update({'read': True})
    db.session.commit()
    return jsonify({'success': True})
