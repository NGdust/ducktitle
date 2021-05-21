if "os" not in dir():
    import os

if 'DEBUG' in os.environ:
    import sentry_sdk
    sentry_sdk.init(os.environ.get('SENTRY_DSN'))