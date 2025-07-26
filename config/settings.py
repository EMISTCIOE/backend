# ruff: noqa
"""
Django settings for tcioe project.
"""

from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
APPS_DIR = BASE_DIR / "src"
env = environ.Env()
environ.Env.read_env(str(BASE_DIR / ".env"))


# SECURITY SETTINGS
# ------------------------------------------------------------------------------
DEBUG = env.bool("DEBUG", False)
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="sydPDD94R0UBhmbBTsXrQ4QDskUY3cPo6cmaa9YorUYNsbzgJqDgnEONnuGpxQ4x",
)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])

CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS")
CORS_ALLOWED_ORGINS = env.list("CORS_ALLOWED_ORIGINS")


CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=["https://api.tcioe.edu.np"],
)


CSP_FRAME_ANCESTORS = [
    "'self'",
    "http://localhost:3000",
    "https://tcioe-cms.vercel.app",
]

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "rest_framework_simplejwt.token_blacklist",
    "ckeditor",
]

LOCAL_APPS = [
    "src.user",
    "src.core",
    "src.website",
    "src.notice",
    "src.journal",
    "src.department",
    "src.curriculum",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# Middlewares
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "csp.middleware.CSPMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "config.urls"


# TEMPLATES
# ------------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# ADMIN
# ------------------------------------------------------------------------------
ADMIN_URL = "admin/"
ADMINS = [("""TCIOE""", "tcioe@edu.np")]


# Databases
# ------------------------------------------------------------------------------
LOCAL = env.bool("LOCAL")

if not LOCAL:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DB_NAME"),
            "USER": env("DB_USER"),
            "PASSWORD": env("DB_PASSWORD"),
            "HOST": env("DB_HOST"),
            "PORT": env("DB_PORT"),
        },
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        },
    }

DATABASES["default"]["ATOMIC_REQUESTS"] = True


# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"


# PASSWORDS
# ------------------------------------------------------------------------------
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
ENCRYPTION_KEY = "UvWTfhGVR2iVUI15zKqF8t54cDu0B_pzyicdearnTDI="


# FIXTURES
# ------------------------------------------------------------------------------
FIXTURE_DIRS = (str(APPS_DIR / "fixtures"),)


# AUTHENTICATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]
AUTH_USER_MODEL = "user.User"


# Internationalization
# ------------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
SITE_ID = 1
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("en", "English"),
    ("np", "Nepali"),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# SECURITY
# ------------------------------------------------------------------------------
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# STATIC
# ------------------------------------------------------------------------------
STATIC_ROOT = str(BASE_DIR / "staticfiles")
STATIC_URL = "/static/"
STATICFILES_DIRS = [str(APPS_DIR / "static")]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


# MEDIA
# ------------------------------------------------------------------------------
MEDIA_ROOT = str(BASE_DIR / "media")
MEDIA_URL = "/media/"


# LOGGING
# ------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}

# django-rest-framework
# -------------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_RENDERER_CLASSES": (
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
        "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": [
        "src.libs.parser.CustomNestedParser",
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ],
    "JSON_UNDERSCOREIZE": {
        "no_underscore_before_number": True,
    },
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "src.libs.exception_handler.custom_exception_handler",
}

NESTED_FORM_PARSER = {"OPTIONS": {"allow_empty": True, "allow_blank": True}}
APPEND_SLASH = False
CORS_URLS_REGEX = r"^/api/.*$"


# API DOCUMENTATION
# ------------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "SCHEMA_COMPONENT_SPLIT_UNDERSCORES": False,
    "TITLE": "TCIOE EMIS Backend API",
    "DESCRIPTION": "Documentation of API endpoints of EMIS Backend",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": True,
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
    ],
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAuthenticated"],
    "SCHEMA_PATH_PREFIX": "/api/v1/cms/",
    "SWAGGER_UI_SETTINGS": {
        "defaultModelsExpandDepth": -1,
    },
}

# JWT Authentication
# ------------------------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=int(env("ACCESS_TOKEN_TIME", default=7))),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(env("REFRESH_TOKEN_TIME", default=10)),
    ),
    "ROTATE_REFRESH_TOKEN": False,
    "BLACKLIST_AFTER_ROTATION": False,
}

# Constants
# ------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
WEBSITE_MEDIA_MAX_UPLOAD_SIZE = int(env("WEBSITE_MEDIA_MAX_UPLOAD_SIZE"))
AUTH_LINK_EXP_TIME = int(env("AUTH_LINK_EXP_TIME"))


# Django Jazzmin
# ------------------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "TCIOE Developers",
    "site_header": "Developers Panel",
    "site_brand": "TCIOE Developers",
    "site_logo": "images/logo.png",
    "custom_css": "css/custom_jazzmin.css",
    "custom_js": "js/custom_jazzmin.js",
}
