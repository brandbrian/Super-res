# settings.py

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_APPS = [
    'my_app',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ... any other installed apps ...
]

STATIC_URL = '/static/'
STATIC_ROOT = '/home/brianbrand/Superres/static'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/brianbrand/Superres/media'


# More settings...
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        # ...
    },
]

# Change these settings for deployment
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = ['brianbrand.pythonanywhere.com']
