from flask import Blueprint, render_template, request
from models.blog import Blog
import markdown

blogs_bp = Blueprint('blogs', __name__)


@blogs_bp.route('/')
def blog_list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()

    query = Blog.query.filter_by(is_published=True)
    if search:
        query = query.filter(Blog.title.ilike(f'%{search}%'))

    blogs = query.order_by(Blog.created_at.desc()).all()
    return render_template('public/blogs.html', blogs=blogs)


@blogs_bp.route('/<slug>')
def blog_detail(slug):
    blog = Blog.query.filter_by(slug=slug, is_published=True).first_or_404()

    md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc', 'sane_lists'])
    content_html = md.convert(blog.content or '')

    related = Blog.query.filter(
        Blog.is_published == True,
        Blog.id != blog.id
    ).order_by(Blog.created_at.desc()).limit(3).all()

    return render_template('public/blog_detail.html', blog=blog, content_html=content_html, related=related)
