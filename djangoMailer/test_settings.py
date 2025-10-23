"""
Test settings for djangoMailer project.
"""

from .settings import *  # noqa

# Use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Remove django_crontab from INSTALLED_APPS for testing
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'django_crontab']

# Disable CSRF for testing
CSRF_COOKIE_SECURE = False

# Use console email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Secret key for testing
SECRET_KEY = 'test-secret-key-for-testing'

# Debug mode
DEBUG = True
