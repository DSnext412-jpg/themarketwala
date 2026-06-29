import os
import json
import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models.user import User
from models.course import Course, Progress, Bookmark
from models.blog import Blog
from models.purchase import Purchase
from models.notification import Notification
from utils.helpers import slugify
from services.storage_service import upload_file, delete_file, list_files, get_bucket

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.before_request
def check_admin():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.home'))


@admin_bp.route('/')
def overview():
    user_count = User.query.count()
    course_count = Course.query.count()
    blog_count = Blog.query.count()
    purchase_count = Purchase.query.filter_by(status='completed').count()
    revenue = db.session.query(db.func.sum(Purchase.amount)).filter_by(status='completed').scalar() or 0

    recent_purchases = Purchase.query.filter_by(status='completed').order_by(
        Purchase.purchased_at.desc()).limit(10).all()

    return render_template('admin/overview.html',
                           user_count=user_count,
                           course_count=course_count,
                           blog_count=blog_count,
                           purchase_count=purchase_count,
                           revenue=revenue,
                           recent_purchases=recent_purchases)


@admin_bp.route('/users')
def users():
    search = request.args.get('search', '').strip()
    query = User.query.join(Purchase).filter(Purchase.status == 'completed')
    if search:
        query = query.filter(User.name.ilike(f'%{search}%') | User.email.ilike(f'%{search}%'))
    users = query.order_by(User.created_at.desc()).all()

    user_purchases = {}
    for user in users:
        user_purchases[user.id] = Purchase.query.filter_by(
            user_id=user.id, status='completed'
        ).order_by(Purchase.purchased_at.desc()).all()

    return render_template('admin/users.html', users=users, user_purchases=user_purchases)


@admin_bp.route('/users/role', methods=['POST'])
def change_user_role():
    user_id = request.form.get('user_id', type=int)
    role = request.form.get('role', 'student')
    user = db.session.get(User, user_id)
    if user and user.id != current_user.id:
        user.role = role
        db.session.commit()
        flash(f'User role updated to {role}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/delete', methods=['POST'])
def delete_user():
    user_id = request.form.get('user_id', type=int)
    user = db.session.get(User, user_id)
    if user and user.id != current_user.id:
        Notification.query.filter_by(user_id=user.id).delete()
        Bookmark.query.filter_by(user_id=user.id).delete()
        Progress.query.filter_by(user_id=user.id).delete()
        Purchase.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        flash('User deleted.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/courses')
def courses():
    all_courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template('admin/courses.html', courses=all_courses)


@admin_bp.route('/courses/create', methods=['GET', 'POST'])
def create_course():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = slugify(title) or 'course'
        description = request.form.get('description', '').strip()
        content = request.form.get('content', '')
        category = request.form.get('category', '').strip()
        difficulty = request.form.get('difficulty', 'beginner')
        price = request.form.get('price', 0, type=float)
        reading_time = request.form.get('reading_time', '').strip()
        lecture_times = request.form.get('lecture_times', '')
        drive_link = request.form.get('drive_link', '').strip()
        live_meeting_link = request.form.get('live_meeting_link', '').strip()
        tags = request.form.get('tags', '').strip()
        is_published = request.form.get('is_published') in ('on', '1', True)

        existing = Course.query.filter_by(slug=slug).first()
        if existing:
            slug = f'{slug}-{int(datetime.datetime.utcnow().timestamp())}'

        course = Course(
            title=title, slug=slug, description=description, content=content,
            category=category, difficulty=difficulty, price=price,
            reading_time=reading_time, lecture_times=lecture_times,
            drive_link=drive_link, live_meeting_link=live_meeting_link,
            tags=tags, is_published=is_published
        )

        if 'thumbnail' in request.files:
            file = request.files['thumbnail']
            if file and file.filename:
                url = upload_file(file.read(), file.filename, 'courses')
                if url:
                    course.thumbnail = url

        db.session.add(course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('admin.courses'))

    return render_template('admin/course_form.html', course=None)


@admin_bp.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    course = db.session.get(Course, course_id)
    if not course:
        flash('Course not found.', 'error')
        return redirect(url_for('admin.courses'))

    if request.method == 'POST':
        course.title = request.form.get('title', course.title).strip()
        course.description = request.form.get('description', course.description).strip()
        course.content = request.form.get('content', course.content)
        course.category = request.form.get('category', course.category).strip()
        course.difficulty = request.form.get('difficulty', course.difficulty)
        course.price = request.form.get('price', course.price, type=float)
        course.reading_time = request.form.get('reading_time', course.reading_time).strip()
        course.lecture_times = request.form.get('lecture_times', course.lecture_times)
        course.drive_link = request.form.get('drive_link', course.drive_link).strip()
        course.live_meeting_link = request.form.get('live_meeting_link', course.live_meeting_link).strip()
        course.tags = request.form.get('tags', course.tags).strip()
        course.is_published = request.form.get('is_published') in ('on', '1', True)

        if 'thumbnail' in request.files:
            file = request.files['thumbnail']
            if file and file.filename:
                url = upload_file(file.read(), file.filename, 'courses')
                if url:
                    course.thumbnail = url

        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('admin.courses'))

    return render_template('admin/course_form.html', course=course)


@admin_bp.route('/courses/toggle-publish', methods=['POST'])
def toggle_course_publish():
    course_id = request.form.get('course_id', type=int)
    course = db.session.get(Course, course_id)
    if course:
        course.is_published = not course.is_published
        db.session.commit()
        flash(f'Course {"published" if course.is_published else "unpublished"}.', 'success')
    return redirect(url_for('admin.courses'))


@admin_bp.route('/courses/delete', methods=['POST'])
def delete_course():
    course_id = request.form.get('course_id', type=int)
    course = db.session.get(Course, course_id)
    if course:
        Bookmark.query.filter_by(course_id=course.id).delete()
        Progress.query.filter_by(course_id=course.id).delete()
        Purchase.query.filter_by(course_id=course.id).delete()
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted.', 'success')
    return redirect(url_for('admin.courses'))


@admin_bp.route('/blogs')
def blogs():
    all_blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    return render_template('admin/blogs.html', blogs=all_blogs)


@admin_bp.route('/blogs/create', methods=['GET', 'POST'])
def create_blog():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = slugify(title) or 'blog'
        content = request.form.get('content', '')
        excerpt = request.form.get('excerpt', '').strip()
        seo_title = request.form.get('seo_title', '').strip()
        seo_description = request.form.get('seo_description', '').strip()
        is_published = request.form.get('is_published') in ('on', '1', True)

        existing = Blog.query.filter_by(slug=slug).first()
        if existing:
            slug = f'{slug}-{int(datetime.datetime.utcnow().timestamp())}'

        blog = Blog(
            title=title, slug=slug, content=content, excerpt=excerpt,
            seo_title=seo_title, seo_description=seo_description,
            is_published=is_published
        )

        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file and file.filename:
                url = upload_file(file.read(), file.filename, 'blogs')
                if url:
                    blog.featured_image = url

        db.session.add(blog)
        db.session.commit()
        flash('Blog created successfully!', 'success')
        return redirect(url_for('admin.blogs'))

    return render_template('admin/blog_form.html', blog=None)


@admin_bp.route('/blogs/edit/<int:blog_id>', methods=['GET', 'POST'])
def edit_blog(blog_id):
    blog = db.session.get(Blog, blog_id)
    if not blog:
        flash('Blog not found.', 'error')
        return redirect(url_for('admin.blogs'))

    if request.method == 'POST':
        blog.title = request.form.get('title', blog.title).strip()
        blog.content = request.form.get('content', blog.content)
        blog.excerpt = request.form.get('excerpt', blog.excerpt).strip()
        blog.seo_title = request.form.get('seo_title', blog.seo_title).strip()
        blog.seo_description = request.form.get('seo_description', blog.seo_description).strip()
        blog.is_published = request.form.get('is_published') in ('on', '1', True)

        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file and file.filename:
                url = upload_file(file.read(), file.filename, 'blogs')
                if url:
                    blog.featured_image = url

        db.session.commit()
        flash('Blog updated successfully!', 'success')
        return redirect(url_for('admin.blogs'))

    return render_template('admin/blog_form.html', blog=blog)


@admin_bp.route('/blogs/toggle-publish', methods=['POST'])
def toggle_blog_publish():
    blog_id = request.form.get('blog_id', type=int)
    blog = db.session.get(Blog, blog_id)
    if blog:
        blog.is_published = not blog.is_published
        db.session.commit()
        flash(f'Blog {"published" if blog.is_published else "unpublished"}.', 'success')
    return redirect(url_for('admin.blogs'))


@admin_bp.route('/blogs/delete', methods=['POST'])
def delete_blog():
    blog_id = request.form.get('blog_id', type=int)
    blog = db.session.get(Blog, blog_id)
    if blog:
        db.session.delete(blog)
        db.session.commit()
        flash('Blog deleted.', 'success')
    return redirect(url_for('admin.blogs'))


@admin_bp.route('/analytics')
def analytics():
    total_users = User.query.count()
    total_courses = Course.query.count()
    total_purchases = Purchase.query.filter_by(status='completed').count()
    total_revenue = db.session.query(db.func.sum(Purchase.amount)).filter_by(status='completed').scalar() or 0

    purchases_over_time = db.session.query(
        db.func.date(Purchase.purchased_at),
        db.func.count(Purchase.id)
    ).filter_by(status='completed').group_by(db.func.date(Purchase.purchased_at)).order_by(
        db.func.date(Purchase.purchased_at)
    ).limit(30).all()

    course_completion = db.session.query(
        Course.title, db.func.count(Progress.id)
    ).join(Progress, Course.id == Progress.course_id).filter(
        Progress.completed == True
    ).group_by(Course.title).all()

    return render_template('admin/analytics.html',
                           total_users=total_users,
                           total_courses=total_courses,
                           total_purchases=total_purchases,
                           total_revenue=total_revenue,
                           purchases_over_time=purchases_over_time,
                           course_completion=course_completion)


@admin_bp.route('/media')
def media():
    files = list_files()
    if not files:
        files = []
    return render_template('admin/media.html', files=files)


@admin_bp.route('/media/upload', methods=['POST'])
def upload_media():
    if 'file' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('admin.media'))

    file = request.files['file']
    if file and file.filename:
        folder = request.form.get('folder', 'courses')
        url = upload_file(file.read(), file.filename, folder)
        if url:
            flash('File uploaded to Supabase!', 'success')
        else:
            flash('Upload failed. Check Supabase storage config.', 'error')
    return redirect(url_for('admin.media'))


@admin_bp.route('/media/delete', methods=['POST'])
def delete_media():
    file_path = request.form.get('file_path', '')
    if delete_file(file_path):
        flash('File deleted from Supabase.', 'success')
    else:
        flash('Could not delete file.', 'error')
    return redirect(url_for('admin.media'))


@admin_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        flash('Settings updated (placeholder). Integrate with a config model for persistence.', 'success')
        return redirect(url_for('admin.settings'))
    return render_template('admin/settings.html')


@admin_bp.route('/export')
def export_data():
    data = {
        'users': [u.to_dict() for u in User.query.all()],
        'courses': [c.to_dict() for c in Course.query.all()],
        'blogs': [b.to_dict() for b in Blog.query.all()],
        'purchases': [p.to_dict() for p in Purchase.query.all()],
    }
    return jsonify(data)
