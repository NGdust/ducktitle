from .base import *

ALLOWED_HOSTS = ['*']

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

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_BEAT_SCHEDULE = {
    'task': {
        'task': 'user.tasks.updateLimitVideoUsers',
        'schedule': 15.0
    }
}