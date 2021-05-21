import os
from flasgger import Swagger, swag_from

class Config:
    UPLOAD_FOLDER = os.getcwd() + os.environ.get('UPLOAD_FOLDER')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_EXTENSIONS = ['mp4', 'mov', 'm4v', 'MP4', 'MOV', 'm4v']


class ConfigDev(Config):
    HOST_AUTH = os.environ.get('WEBSITE_URL')
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456789@localhost:5432/video'


class ConfigProd(Config):
    HOST_AUTH = os.environ.get('WEBSITE_URL')
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:5432/{}'.format(os.environ.get('VIDEO_DATABASE_USER'),
                                                                     os.environ.get('VIDEO_DATABASE_PASSWORD'),
                                                                     os.environ.get('VIDEO_DATABASE_HOST'),
                                                                     os.environ.get('VIDEO_DATABASE_DB'))
    if 'DEBUG' in os.environ:
        import sentry_sdk
        sentry_sdk.init(os.environ.get('SENTRY_DSN'))

    if os.environ.get('DEBUG') == 'test':
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'



configSwagger = Swagger.DEFAULT_CONFIG
configSwagger['specs_route'] = '/video/swagger/'
configSwagger['static_url_path'] = '/video//flasgger_static'
configSwagger['specs'][0]['route'] = '/video/apispec_1.json'