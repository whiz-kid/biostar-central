from biostar4.settings.base import *

# The database needs to change to postgresql
__NAME = 'travis_ci_test'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': __NAME,
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': 5432,
     }
}