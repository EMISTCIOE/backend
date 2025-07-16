from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


ALLOWED_EXTENSIONS = {
    "IMAGE": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "DOCUMENT": [".pdf"],
}


def validate_notice_media_file(file, media_type):
    """Validate file extension based on media type."""

    ext = file.name.split(".")[-1].lower()
    if media_type not in ALLOWED_EXTENSIONS:
        raise ValidationError(_("Invalid media type selected."))

    if ext not in [e.strip(".") for e in ALLOWED_EXTENSIONS[media_type]]:
        raise ValidationError(_("Unsupported file type for the selected media type."))
