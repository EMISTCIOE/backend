import os

from rest_framework.serializers import ValidationError

# 5 MB in bytes
DEPARTMENT_DOWNLOAD_FILE_SIZE_LIMIT = 5 * 1024 * 1024


def validate_department_download_file(value):
    # 1. Check file size (max 5MB)
    max_size = DEPARTMENT_DOWNLOAD_FILE_SIZE_LIMIT
    if value.size > max_size:
        raise ValidationError("File size should not exceed 5 MB.")

    # 2. Check file extension
    ext = os.path.splitext(value.name)[1].lower()  # get file extension
    allowed_extensions = [".pdf", ".docx", ".png", ".jpg", ".jpeg"]
    if ext not in allowed_extensions:
        raise ValidationError(
            f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}.",
        )


MAX_PHOTO_SIZE = 2 * 1024 * 1024  # 2MB in bytes
ALLOWED_PHOTO_EXTENSIONS = [".jpg", ".jpeg", ".png"]


def validate_photo_thumbnail(file):
    """
    Validate that the file is an image with allowed extensions and <= 2MB.
    """
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_PHOTO_EXTENSIONS:
        raise ValidationError(
            f"Unsupported file type: {ext}. Allowed types are {', '.join(ALLOWED_PHOTO_EXTENSIONS)}",
        )

    if file.size > MAX_PHOTO_SIZE:
        raise ValidationError("File size must not exceed 2MB.")
