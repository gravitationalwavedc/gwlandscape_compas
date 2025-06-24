from .base import *

DEBUG = False

SITE_URL = "https://gwlandscape.org.au"

STATIC_URL = "/static/"

ALLOWED_HOSTS = ["*"]

EMAIL_HOST = "mail.swin.edu.au"
EMAIL_PORT = 25

GWCLOUD_JOB_CONTROLLER_API_URL = "https://jobcontroller.adacs.org.au/job/apiv1"
CELERY_BROKER_URL = "redis://redis:6379"
CELERY_RESULT_BACKEND = "redis://redis:6379"

# On both login and logout, redirect to the frontend react app
LOGIN_REDIRECT_URL = "/"
LOGIN_REDIRECT_URL = "/"

# adacs-sso settings
ADACS_SSO_CLIENT_NAME = "gwlandscape_compas"
ADACS_SSO_AUTH_HOST = "https://sso.adacs.org.au"

try:
    from .environment import *
except ImportError:
    pass
