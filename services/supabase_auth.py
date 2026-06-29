import requests
from flask import current_app, session
from extensions import db
from models.user import User


def _headers():
    return {
        'apikey': current_app.config['SUPABASE_KEY'],
        'Content-Type': 'application/json',
    }


def _auth_headers():
    headers = _headers()
    access_token = session.get('supabase_access_token')
    if access_token:
        headers['Authorization'] = f'Bearer {access_token}'
    return headers


def sign_up(email, password, name):
    resp = requests.post(
        f'{current_app.config["SUPABASE_URL"]}/auth/v1/signup',
        headers=_headers(),
        json={'email': email, 'password': password, 'data': {'name': name}}
    )
    if resp.status_code not in (200, 201):
        error = resp.json()
        return None, error.get('msg', 'Signup failed')

    data = resp.json()
    supabase_uid = data.get('id')
    email_confirmed = False

    user = User.query.filter_by(supabase_uid=supabase_uid).first()
    if not user:
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name=name, email=email, supabase_uid=supabase_uid, role='student')
            db.session.add(user)
        else:
            user.supabase_uid = supabase_uid
        db.session.commit()

    access_token = data.get('access_token')
    if access_token:
        session['supabase_access_token'] = access_token
        session['supabase_refresh_token'] = data.get('refresh_token', '')
        session['supabase_user_id'] = supabase_uid
        session.permanent = True

    return user, None


def sign_in(email, password):
    resp = requests.post(
        f'{current_app.config["SUPABASE_URL"]}/auth/v1/token?grant_type=password',
        headers=_headers(),
        json={'email': email, 'password': password}
    )
    if resp.status_code != 200:
        error = resp.json()
        return None, error.get('msg', 'Invalid email or password')

    data = resp.json()
    supabase_uid = data['user']['id']
    email = data['user']['email']
    name = data['user'].get('user_metadata', {}).get('name', email.split('@')[0])

    user = User.query.filter_by(supabase_uid=supabase_uid).first()
    if not user:
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name=name, email=email, supabase_uid=supabase_uid, role='student')
            db.session.add(user)
        else:
            user.supabase_uid = supabase_uid
        db.session.commit()

    access_token = data.get('access_token')
    if access_token:
        session['supabase_access_token'] = access_token
        session['supabase_refresh_token'] = data.get('refresh_token', '')
        session['supabase_user_id'] = supabase_uid
        session.permanent = True

    return user, None


def sign_out():
    try:
        requests.post(
            f'{current_app.config["SUPABASE_URL"]}/auth/v1/logout',
            headers=_auth_headers()
        )
    except Exception:
        pass
    session.pop('supabase_access_token', None)
    session.pop('supabase_refresh_token', None)
    session.pop('supabase_user_id', None)


def get_supabase_user():
    supabase_uid = session.get('supabase_user_id')
    if not supabase_uid:
        return None
    return User.query.filter_by(supabase_uid=supabase_uid).first()



