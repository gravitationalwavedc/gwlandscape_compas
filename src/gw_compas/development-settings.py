from .base import *

INSTALLED_APPS += ('corsheaders', )
CORS_ORIGIN_ALLOW_ALL = True

MIDDLEWARE.append('corsheaders.middleware.CorsMiddleware')

SITE_URL = "http://localhost:3000"

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EXTERNAL_STORAGE_PATH = os.path.join(BASE_DIR, 'files')
FILE_UPLOAD_TEMP_DIR = os.path.join(EXTERNAL_STORAGE_PATH, 'upload')

try:
    from .local import *
except:
    pass
