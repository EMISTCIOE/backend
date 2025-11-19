"""
EMIS Utilities
Password encryption/decryption helpers
"""

from cryptography.fernet import Fernet
from django.conf import settings


def get_encryption_key():
    """Get or generate encryption key"""
    # In production, store this in environment variables
    key = getattr(settings, "VPS_ENCRYPTION_KEY", None)
    if not key:
        # Generate a key (for development only)
        key = Fernet.generate_key()
    if isinstance(key, str):
        key = key.encode()
    return key


def encrypt_password(password: str) -> str:
    """Encrypt password using Fernet"""
    fernet = Fernet(get_encryption_key())
    encrypted = fernet.encrypt(password.encode())
    return encrypted.decode()


def decrypt_password(encrypted_password: str) -> str:
    """Decrypt password using Fernet"""
    fernet = Fernet(get_encryption_key())
    decrypted = fernet.decrypt(encrypted_password.encode())
    return decrypted.decode()


def generate_otp() -> str:
    """Generate 6-digit OTP"""
    import random
    return str(random.randint(100000, 999999))
