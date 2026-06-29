import re
import uuid


def slugify(text):
    if not text:
        return ''
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def generate_unique_filename(original_name):
    ext = original_name.rsplit('.', 1)[-1] if '.' in original_name else ''
    return f'{uuid.uuid4().hex}.{ext}' if ext else uuid.uuid4().hex
