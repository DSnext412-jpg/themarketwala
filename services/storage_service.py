import os
import uuid
from flask import current_app

_supabase_client = None
_use_supabase = True


def get_supabase():
    global _supabase_client, _use_supabase
    if not _use_supabase:
        return None
    if _supabase_client is None:
        try:
            from supabase import create_client
            url = current_app.config.get('SUPABASE_URL', '')
            key = current_app.config.get('SUPABASE_KEY', '')
            if url and key and key.startswith('ey'):
                _supabase_client = create_client(url, key)
            else:
                _use_supabase = False
        except Exception:
            _use_supabase = False
    return _supabase_client


def get_bucket():
    return current_app.config.get('SUPABASE_BUCKET', 'market-wala')


def _local_path(folder, filename):
    folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(folder_path, exist_ok=True)
    return os.path.join(folder_path, filename)


def upload_file(file_data, filename, folder='courses'):
    ext = filename.rsplit('.', 1)[-1] if '.' in filename else ''
    unique_name = f'{uuid.uuid4().hex}.{ext}'

    client = get_supabase()
    if client:
        try:
            path = f'{folder}/{unique_name}'
            client.storage.from_(get_bucket()).upload(
                path=path, file=file_data,
                file_options={'content-type': 'application/octet-stream'}
            )
            return client.storage.from_(get_bucket()).get_public_url(path)
        except Exception as e:
            current_app.logger.error(f'Supabase upload error: {e}')

    path = _local_path(folder, unique_name)
    with open(path, 'wb') as f:
        f.write(file_data)
    return f'/uploads/{folder}/{unique_name}'


def delete_file(path_or_url):
    client = get_supabase()
    if client:
        try:
            bucket_url = f'{current_app.config.get("SUPABASE_URL")}/storage/v1/object/public/{get_bucket()}/'
            path = path_or_url
            if bucket_url in path_or_url:
                path = path_or_url.replace(bucket_url, '')
            client.storage.from_(get_bucket()).remove([path])
            return True
        except Exception as e:
            current_app.logger.error(f'Supabase delete error: {e}')

    full_path = os.path.join(
        os.path.dirname(current_app.root_path), 'uploads', path_or_url.lstrip('/uploads/')
    )
    if os.path.exists(full_path):
        os.remove(full_path)
        return True
    return False


def list_files(folder=''):
    client = get_supabase()
    if client:
        try:
            results = client.storage.from_(get_bucket()).list(path=folder)
            files = []
            for item in results:
                name = item.get('name', '')
                if name:
                    path = f'{folder}/{name}' if folder else name
                    files.append({
                        'name': name,
                        'path': path,
                        'url': client.storage.from_(get_bucket()).get_public_url(path),
                        'size': item.get('metadata', {}).get('size', 0),
                    })
            return files
        except Exception as e:
            current_app.logger.error(f'Supabase list error: {e}')

    media_dir = os.path.join(current_app.config['UPLOAD_FOLDER'])
    files = []
    for root, dirs, filenames in os.walk(media_dir):
        for f in filenames:
            rel_path = os.path.relpath(os.path.join(root, f), os.path.dirname(current_app.root_path))
            files.append({
                'name': f,
                'path': '/' + rel_path.replace('\\', '/'),
                'url': '/' + rel_path.replace('\\', '/'),
                'size': os.path.getsize(os.path.join(root, f)),
            })
    return files
