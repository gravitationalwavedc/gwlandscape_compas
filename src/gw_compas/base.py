"""
Django settings for gwcloud_auth project.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^zzul@u)rxayk67^%3kf^59!pw&-vfv0lnv6#6h)w6!eyjzz!g'
JOB_CONTROLLER_JWT_SECRET = SECRET_KEY
AUTH_SERVICE_JWT_SECRET = SECRET_KEY
DB_SEARCH_SERVICE_JWT_SECRET = SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'compasui.apps.CompasConfig',
    'graphene_django',
    'django_jenkins',
    'publications',
    'django_filters'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gw_compas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gw_compas.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static-files/')

MEDIA_ROOT = os.path.join(BASE_DIR, "../files/")

MEDIA_URL = '/compas/files/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static/"),
]

EMAIL_FROM = 'no-reply@gwlandscape.org.au'
EMAIL_HOST = 'mail.swin.edu.au'
EMAIL_PORT = 25

GRAPHENE = {
    'SCHEMA': 'gw_compas.schema.schema',
    'SCHEMA_OUTPUT': 'react/data/schema.json',  # defaults to schema.json,
    'SCHEMA_INDENT': 2,  # Defaults to None (displays all data on a single line),
    'MIDDLEWARE': [
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
    ],
}

AUTHENTICATION_BACKENDS = [
    'graphql_jwt.backends.JSONWebTokenBackend',
    'django.contrib.auth.backends.ModelBackend',
]


def jwt_get_user_by_payload_override(payload):
    from .jwt_tools import jwt_get_user_by_payload
    return jwt_get_user_by_payload(payload)


GRAPHQL_JWT = {
    # Our implementation of JWT_PAYLOAD_GET_USERNAME_HANDLER returns a full user object rather than just a username
    'JWT_PAYLOAD_GET_USERNAME_HANDLER': jwt_get_user_by_payload_override,
    # Internally this usually takes a username returned by JWT_PAYLOAD_GET_USERNAME_HANDLER, but as we're returning
    # the full user object from JWT_PAYLOAD_GET_USERNAME_HANDLER, we don't do any processing, and simply just return
    # the passed user object.
    'JWT_GET_USER_BY_NATURAL_KEY_HANDLER': lambda x: x,
    'JWT_VERIFY_EXPIRATION': True
}

# URL of the job controller - note: No trailing slash
GWCLOUD_JOB_CONTROLLER_API_URL = "https://jobcontroller.adacs.org.au/job/apiv1"
GWCLOUD_AUTH_API_URL = "http://localhost:8000/graphql"
GWCLOUD_DB_SEARCH_API_URL = "http://gwcloud-db-search:8000/graphql"

CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TASK_SOFT_TIME_LIMIT = 5
CELERY_TASK_TIME_LIMIT = 7

COMPAS_IO_PATH = os.path.join(MEDIA_ROOT, 'jobs/')

PERMITTED_PUBLICATION_MANAGEMENT_USER_IDS = []

COMPAS_DATASET_MODEL_UPLOAD_TOKEN_EXPIRY = 60*60*24     # User has one day to upload the file for the job

# The expiry of FileDownloadTokens (in seconds)
FILE_DOWNLOAD_TOKEN_EXPIRY = 60*60*24

EXTERNAL_STORAGE_PATH = '/files'
FILE_UPLOAD_TEMP_DIR = os.path.join(EXTERNAL_STORAGE_PATH, 'upload')