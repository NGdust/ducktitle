from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

ALLOWED_HOSTS = ['*']
DEBUG = True

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ.get('AUTH_DATABASE_NAME'),
            'HOST': os.environ.get('AUTH_DATABASE_HOST'),
            'PORT': 5432,
            'USER': os.environ.get('AUTH_DATABASE_USER'),
            'PASSWORD': os.environ.get('AUTH_DATABASE_PASSWORD'),
        }
    }

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

sentry_sdk.init(dsn=os.environ.get('SENTRY_DSN'), integrations=[DjangoIntegration()])