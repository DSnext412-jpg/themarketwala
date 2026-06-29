from authlib.integrations.flask_client import OAuth
from flask import current_app

oauth = OAuth()

google = None


def init_oauth(app):
    global google
    oauth.init_app(app)

    client_id = app.config.get('GOOGLE_CLIENT_ID')
    client_secret = app.config.get('GOOGLE_CLIENT_SECRET')

    if client_id and client_secret:
        google = oauth.register(
            name='google',
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'},
        )
