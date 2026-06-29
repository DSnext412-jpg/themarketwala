import os
import markdown
from flask import Flask, render_template, request, jsonify, current_app
from config import DevelopmentConfig, ProductionConfig, TestingConfig
from extensions import db, login_manager, migrate, csrf, session_ext, cors, mail



def create_app(config_name=None):
    app = Flask(__name__)

    env = os.getenv('FLASK_ENV', 'development')
    if config_name == 'testing':
        app.config.from_object(TestingConfig)
    elif env == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    initialize_extensions(app)
    register_blueprints(app)
    register_template_filters(app)
    register_error_handlers(app)
    register_context_processors(app)

    create_upload_folders(app)

    return app


def initialize_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    session_ext.init_app(app)
    cors.init_app(app)
    mail.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return db.session.get(User, int(user_id))

    @login_manager.request_loader
    def load_user_from_request(request):
        from flask import session
        from models.user import User
        supabase_uid = session.get('supabase_user_id')
        if supabase_uid:
            return User.query.filter_by(supabase_uid=supabase_uid).first()
        return None


def register_blueprints(app):
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.courses import courses_bp
    from routes.blogs import blogs_bp
    from routes.student import student_bp
    from routes.admin import admin_bp
    from routes.checkout import checkout_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(courses_bp, url_prefix='/courses')
    app.register_blueprint(blogs_bp, url_prefix='/blogs')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(checkout_bp, url_prefix='/checkout')


def register_template_filters(app):
    @app.template_filter('markdown')
    def render_markdown(text):
        if not text:
            return ''
        extensions = ['extra', 'codehilite', 'toc', 'sane_lists']
        md = markdown.Markdown(extensions=extensions)
        return md.convert(text)

    @app.template_filter('truncate_words')
    def truncate_words(text, words=30):
        if not text:
            return ''
        word_list = text.split()
        if len(word_list) <= words:
            return text
        return ' '.join(word_list[:words]) + '...'

    @app.template_filter('format_date')
    def format_date(date, fmt='%b %d, %Y'):
        if not date:
            return ''
        return date.strftime(fmt)


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return render_template('public/404.html'), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('public/403.html'), 403

    @app.errorhandler(500)
    def server_error(error):
        return render_template('public/500.html'), 500


def register_context_processors(app):
    @app.context_processor
    def inject_globals():
        return {
            'site_name': 'The Market Wala',
            'current_year': 2026,
            'razorpay_key_id': app.config.get('RAZORPAY_KEY_ID', ''),
        }


def create_upload_folders(app):
    folders = ['courses', 'blogs', 'avatars']
    for folder in folders:
        path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(path, exist_ok=True)


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
