from .base import *

INSTALLED_APPS += ("corsheaders",)
# For requests to include credentials (i.e., http-only cookies) the
# CORS_ALLOWED_ORIGINS must not be ['*']
CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]
CORS_ALLOW_CREDENTIALS = True

MIDDLEWARE.append("corsheaders.middleware.CorsMiddleware")

SITE_URL = "http://localhost:3000"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

EXTERNAL_STORAGE_PATH = os.path.join(BASE_DIR, "files")
FILE_UPLOAD_TEMP_DIR = os.path.join(EXTERNAL_STORAGE_PATH, "upload")

# On both login and logout, redirect to the frontend react app
LOGIN_REDIRECT_URL = "http://localhost:3000/"
LOGIN_REDIRECT_URL = "http://localhost:3000/"

# adacs-sso settings
ADACS_SSO_CLIENT_NAME = "gwlandscape_compas_dev"
ADACS_SSO_AUTH_HOST = "http://localhost:8000"

try:
    from .local import *
except:
    pass
