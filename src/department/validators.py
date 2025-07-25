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
            f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}."
        )
