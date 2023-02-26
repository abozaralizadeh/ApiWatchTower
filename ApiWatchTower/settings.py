"""
Django settings for ApiWatchTower project.

Based on by 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import posixpath
from .get_env_settings import get_env_value

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9eb09dcc-aa29-44db-8daa-12fa6e7f8359'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Application references
# https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-INSTALLED_APPS
INSTALLED_APPS = [
    'jet.dashboard',
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'HealthChecker.apps.HealthCheckerConfig',
]

# Middleware framework
# https://docs.djangoproject.com/en/2.1/topics/http/middleware/
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
]

X_FRAME_OPTIONS = 'SAMEORIGIN'
ROOT_URLCONF = 'ApiWatchTower.urls'

# Template configuration
# https://docs.djangoproject.com/en/2.1/topics/templates/
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates/')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ApiWatchTower.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    'develop': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_env_value('AWT_PG_DBNAME', 'AWT'),
        'USER': get_env_value('AWT_PG_USERNAME', 'postgres'),
        'PASSWORD': get_env_value('AWT_PG_PASSWORD', 'postgres'),
        'HOST': get_env_value('AWT_PG_HOST', 'postgres'),
        'PORT': get_env_value('AWT_PG_PORT', 5432)
    }
}

DEFAULT_AUTO_FIELD='django.db.models.AutoField'

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators
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

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'azure_ad_auth.backends.AzureActiveDirectoryBackend',
)

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = get_env_value('AWT_LANGUAGE_CODE', 'it')
TIME_ZONE = get_env_value('AWT_TIME_ZONE', 'Europe/Rome')
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = '/static/'
# STATIC_ROOT = posixpath.join(*(BASE_DIR.split(os.path.sep) + ['static']))
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# celery

AWT_REDIS_HOST = get_env_value('AWT_REDIS_HOST', 'redis')
AWT_REDIS_PORT = get_env_value('AWT_REDIS_PORT', 6379)

CELERY_BROKER_URL = 'redis://{}:{}'.format(AWT_REDIS_HOST, AWT_REDIS_PORT)
CELERY_RESULT_BACKEND = 'redis://{}:{}'.format(AWT_REDIS_HOST, AWT_REDIS_PORT)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

SESSION_COOKIE_SAMESITE = None

# Azure
LOGIN_REDIRECT_URL = '/admin/'
AAD_TENANT_ID = get_env_value('AAD_TENANT_ID', 'xxxx')
AAD_CLIENT_ID = get_env_value('AAD_CLIENT_ID', 'xxxx')
# AAD_AUTHORITY = ''
# AAD_SCOPE = ''
AAD_RESPONSE_TYPE = get_env_value('AAD_RESPONSE_TYPE', 'id_token')
AAD_EMAIL_FIELD = get_env_value('AAD_EMAIL_FIELD', 'email')
AAD_USER_STATIC_MAPPING = {'is_staff': True}  # , 'is_superuser': True
AAD_USER_MAPPING = {'username': 'email', 'first_name': 'name'}
AAD_GROUP_MAPPING = {'admin': 'admins', }
AAD_GROUP_STATIC_MAPPING = {'members', }
#CELERY_RDBSIG=1
#CELERY_ALWAYS_EAGER = True
try:
    HTTPS = get_env_value('HTTPS')
except:
    HTTPS = 'off'
