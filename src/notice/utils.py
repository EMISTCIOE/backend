import re
import uuid
from pathlib import Path

from .constants import NOTICE_MEDIA_PATH


def slugify_filename(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "-", value).lower()


def notice_media_upload_path(instance, filename):
    """
    Generate a unique file path for uploading notice media.
    Renames the uploaded file using a UUID to avoid filename collisions.
    """
    ext = Path(filename).suffix
    new_filename = f"{uuid.uuid4()}{ext.lower()}"
    return str(Path(NOTICE_MEDIA_PATH) / new_filename)
