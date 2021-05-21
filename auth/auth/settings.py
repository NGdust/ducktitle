import json
import os
import datetime

from loguru import logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '78p+!%lck0bwgttf)=_k*ls_k-b&!#-2jtw92ircp(^blz2&)w'

DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'corsheaders',

    'user',
    'data',
]

AUTH_USER_MODEL = 'user.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'auth.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'auth.wsgi.application'

if 'DATABASE_NAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ.get('DATABASE_NAME'),
            'HOST': os.environ.get('DATABASE_HOST'),
            'PORT': 5432,
            'USER': os.environ.get('DATABASE_USER'),
            'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        }
    }
else:
    if os.environ.get('GITHUB_WORKFLOW'):
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'github_actions',
                'USER': 'postgres',
                'PASSWORD': 'postgres',
                'HOST': '127.0.0.1',
                'PORT': 5432,
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'suptitle_auth',
                'HOST': 'localhost',
                'PORT': 5432,
                'USER': 'postgres',
                'PASSWORD': 'nigative32',
            }
        }

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

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=14)
}

CORS_ORIGIN_ALLOW_ALL = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ]
}

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

REDIS_HOST = 'localhost'
if 'DEBUG' in os.environ:
    REDIS_HOST = 'redis'
REDIS_PORT = 6379
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_BEAT_SCHEDULE = {
    'task': {
        'task': 'user.tasks.updateLimitVideoUsers',
        'schedule': 15.0
    }
}

logger.add("logs/{time}.log", format="{time} {level} {message}", rotation="10 MB", compression="zip")
configPayFilePath = BASE_DIR + "/auth/payConfig.json"
PAY_CONFIG = None
with open(configPayFilePath, "r") as file:
    PAY_CONFIG = json.loads(file.read())

if 'DEBUG' in os.environ and 'SENTRY_DSN' in os.environ:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    sentry_sdk.init(dsn=os.environ.get('SENTRY_DSN'), integrations=[DjangoIntegration()])