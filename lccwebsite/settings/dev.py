from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = "8t_kdc0d!1#59mpdzec_tuo2t@(hgraijx#u@4m2h_49laef@k"
SECRET_KEY = os.environ.get("SECRET_KEY", "8t_kdc0d!1#59mpdzec_tuo2t@")

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get(
            "DB_DATABASE_NAME", os.path.join(BASE_DIR, "db.sqlite3")
        ),
        "USER": os.environ.get("DB_USER", "user"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "password"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

try:
    from .local import *
except ImportError:
    pass
