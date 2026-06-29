from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import User
from utils.validators import validate_email, validate_password
from services.supabase_auth import sign_up, sign_in, sign_out as supabase_sign_out

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        if not email or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('auth/login.html')

        user, error = sign_in(email, password)
        if error or not user:
            flash(error or 'Invalid email or password.', 'error')
            return render_template('auth/login.html')

        login_user(user, remember=remember)
        flash(f'Welcome back, {user.name}!', 'success')

        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        if user.is_admin():
            return redirect(url_for('admin.overview'))
        return redirect(url_for('student.overview'))

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('auth/register.html')

        if not validate_email(email):
            flash('Please enter a valid email address.', 'error')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')

        if not validate_password(password):
            flash('Password must be at least 8 characters with a number and a letter.', 'error')
            return render_template('auth/register.html')

        user, error = sign_up(email, password, name)
        if error or not user:
            flash(error or 'Registration failed. Please try again.', 'error')
            return render_template('auth/register.html')

        login_user(user)
        flash('Account created successfully! Welcome to The Market Wala.', 'success')
        return redirect(url_for('student.overview'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    supabase_sign_out()
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if email:
            try:
                import requests
                requests.post(
                    f'{current_app.config["SUPABASE_URL"]}/auth/v1/recover',
                    headers={
                        'apikey': current_app.config['SUPABASE_KEY'],
                        'Content-Type': 'application/json',
                    },
                    json={'email': email}
                )
            except Exception:
                pass
        flash('If the email exists, a reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')
