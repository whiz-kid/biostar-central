from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core import mail
from biostar4.forum.models import *

import os

def test_email():
    print('---------------------')
    print ("Sending a test email ...")
    print('---------------------')
    with mail.get_connection() as connection:
        subject = "This is a test message from Biostar"
        body = "If you can read this then the server can send emails."
        from1 = settings.DEFAULT_FROM_EMAIL
        to1 = settings.ADMIN_FROM_EMAIL
        mail.EmailMessage(subject, body, from1, [to1], connection=connection).send()


class Command(BaseCommand):
    help = 'Shows the current settings'

    def add_arguments(self, parser):
        parser.add_argument('--testemail',
            action='store_true',dest='test_email', default=False,
            help='Send a test email as well')

    def handle(self, *args, **options):

        setting_module = os.getenv('DJANGO_SETTINGS_MODULE')
        print('---------------------')
        print("DJANGO_SETTINGS_MODULE: {}".format(setting_module))
        print("DEBUG: {}".format(settings.DEBUG))
        print("THEME_DIRS: {}".format(settings.THEME_DIRS))
        print("STATICFILES_DIRS: {}".format(settings.STATICFILES_DIRS))
        print('---------------------')
        print("RECAPTCHA_ENABLED: {}".format(settings.RECAPTCHA_ENABLED))
        print("SECRET_KEY: {}".format(settings.SECRET_KEY))
        print('---------------------')
        print("EMAIL_BACKEND: {}".format(settings.EMAIL_BACKEND))

        #print("SECRET_KEY: {}".format(settings.SECRET_KEY))

        if options.get('test_email'):
            test_email()