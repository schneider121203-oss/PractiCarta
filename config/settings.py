import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-development-key")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = [item.strip() for item in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")]
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
CSRF_TRUSTED_ORIGINS = [item.strip() for item in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if item.strip()]

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "app.accounts", "app.businesses", "app.catalog", "app.analytics", "app.menu_imports",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware", "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware", "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [BASE_DIR / "app" / "templates"], "APP_DIRS": True, "OPTIONS": {"context_processors": ["django.template.context_processors.request", "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "config.wsgi.application"

# SQLite keeps the project immediately runnable; Docker supplies PostgreSQL for shared environments.
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
if os.getenv("DATABASE_URL"):
    from urllib.parse import urlparse
    parsed = urlparse(os.environ["DATABASE_URL"])
    DATABASES["default"] = {"ENGINE": "django.db.backends.postgresql", "NAME": parsed.path.lstrip("/"), "USER": parsed.username, "PASSWORD": parsed.password, "HOST": parsed.hostname, "PORT": parsed.port or 5432}

AUTH_USER_MODEL = "accounts.User"
LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "app" / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "businesses:dashboard"
LOGOUT_REDIRECT_URL = "login"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
GEMINI_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.1-flash-lite")
AWS_GEMINI_SECRET_ID = os.getenv("AWS_GEMINI_SECRET_ID", "")
AWS_SECRETS_REGION = os.getenv("AWS_SECRETS_REGION", "us-east-1")
AWS_SECRETS_PROFILE = os.getenv("AWS_SECRETS_PROFILE", "")
GEMINI_SECRET_JSON_KEY = os.getenv("GEMINI_SECRET_JSON_KEY", "")

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "3600"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
