from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
from models.course import Course, Bookmark, Progress
from models.purchase import Purchase
from extensions import db
import markdown

courses_bp = Blueprint('courses', __name__)


@courses_bp.route('/')
def course_list():
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    difficulty = request.args.get('difficulty', '').strip()

    query = Course.query.filter_by(is_published=True)

    if search:
        query = query.filter(Course.title.ilike(f'%{search}%'))
    if category:
        query = query.filter_by(category=category)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    courses = query.order_by(Course.created_at.desc()).all()

    categories = [c[0] for c in db.session.query(Course.category).filter(Course.is_published == True).distinct().all() if c[0]]
    difficulties = ['beginner', 'intermediate', 'advanced']

    return render_template('public/courses.html', courses=courses, categories=categories, difficulties=difficulties)


@courses_bp.route('/<slug>')
def course_detail(slug):
    course = Course.query.filter_by(slug=slug, is_published=True).first_or_404()

    is_purchased = False
    is_bookmarked = False
    progress = None

    if current_user.is_authenticated:
        purchase = Purchase.query.filter_by(
            user_id=current_user.id, course_id=course.id, status='completed'
        ).first()
        is_purchased = purchase is not None

        bookmark = Bookmark.query.filter_by(user_id=current_user.id, course_id=course.id).first()
        is_bookmarked = bookmark is not None

        progress = Progress.query.filter_by(user_id=current_user.id, course_id=course.id).first()

    content_html = ''
    if is_purchased and course.content:
        md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc', 'sane_lists'])
        content_html = md.convert(course.content)

    related = Course.query.filter(
        Course.is_published == True,
        Course.id != course.id
    ).order_by(Course.created_at.desc()).limit(3).all()

    return render_template('public/course_detail.html',
                           course=course,
                           is_purchased=is_purchased,
                           is_bookmarked=is_bookmarked,
                           progress=progress,
                           content_html=content_html,
                           related=related)
