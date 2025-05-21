from .base import *

DEBUG = False

SITE_URL = "https://gwlandscape.org.au"

STATIC_URL = "/static/"

ALLOWED_HOSTS = ["*"]

EMAIL_HOST = "mail.swin.edu.au"
EMAIL_PORT = 25

GWCLOUD_JOB_CONTROLLER_API_URL = "http://jobcontroller.adacs.org.au/job/apiv1"
GWCLOUD_AUTH_API_URL = "http://gwlandscape.org.au/auth/graphql"
GWCLOUD_DB_SEARCH_API_URL = "http://gwcloud-db-search:8000/graphql"
CELERY_BROKER_URL = "redis://gwlandscape-compas-redis:6379"
CELERY_RESULT_BACKEND = "redis://gwlandscape-compas-redis:6379"

try:
    from .environment import *
except ImportError:
    pass
