import os
from datetime import datetime

from rest_framework.serializers import ValidationError

# 5 MB in bytes
DEPARTMENT_DOWNLOAD_FILE_SIZE_LIMIT = 5 * 1024 * 1024


def validate_campus_download_file(value):
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


def validate_nepali_year(value):
    """
    Validate that the year is in proper Nepali year format (4 digits, reasonable range).
    Nepali years typically range from around 2000 BS to 2200 BS (approx 1943 AD to 2143 AD).
    """
    if not isinstance(value, int):
        raise ValidationError("Year must be an integer.")
    
    # Check if it's a 4-digit number
    if not (1000 <= value <= 9999):
        raise ValidationError("Year must be a 4-digit number.")
    
    # Nepali year range validation (reasonable range for academic purposes)
    current_nepali_year = datetime.now().year + 57  # Approximate conversion to Nepali year
    min_year = 2040  # Around 1983 AD
    max_year = current_nepali_year + 10  # Allow up to 10 years in the future
    
    if not (min_year <= value <= max_year):
        raise ValidationError(
            f"Nepali year must be between {min_year} and {max_year}."
        )
