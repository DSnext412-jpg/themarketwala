from flask import Blueprint, render_template, request
from models.course import Course
from models.blog import Blog

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    featured_courses = Course.query.filter_by(is_published=True).order_by(Course.created_at.desc()).limit(3).all()
    latest_blogs = Blog.query.filter_by(is_published=True).order_by(Blog.created_at.desc()).limit(2).all()
    return render_template('public/home.html', courses=featured_courses, blogs=latest_blogs)


@main_bp.route('/about')
def about():
    return render_template('public/about.html')


@main_bp.route('/contact')
def contact():
    return render_template('public/contact.html')
