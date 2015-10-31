from biostar4.settings.base import *

__NAME = 'biostar_testdb'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': __NAME,
        'USER': 'testuser',
        'PASSWORD': 'testpassword',
        'HOST': 'localhost',
        'PORT': 5432,
     }
}