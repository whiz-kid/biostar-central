from biostar.settings.base import *
import os


def abspath(*args):
    """Generates absolute paths"""
    return os.path.abspath(os.path.join(*args))

TEMPLATE_DIR1 = abspath(HOME_DIR, 'biostar', 'server', 'templates')
TEMPLATE_DIR2 = abspath(HOME_DIR, 'starbase',  'templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR1, TEMPLATE_DIR2],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'string_if_invalid': "*** MISSING ***",
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'biostar.server.context.shortcuts',
            ],
        },
    },
]

STATIC_DIR1 = abspath(HOME_DIR, 'biostar', 'static')
STATIC_DIR2 = abspath(HOME_DIR, 'starbase', 'static')

STATICFILES_DIRS = [STATIC_DIR1, STATIC_DIR2]

ROOT_URLCONF = 'starbase.urls'

USE_CAPTCHA = False
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY', 'ABC')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY', 'ABC')
RECAPTCHA_USE_SSL = True
NOCAPTCHA = True