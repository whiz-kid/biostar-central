from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core import mail

import os

def sep():
    print('---------------------')


def test_email():
    sep()
    print ("Sending a test email ...")
    sep()
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
        sep()
        print("DJANGO_SETTINGS_MODULE: {}".format(setting_module))
        print("DEBUG: {}".format(settings.DEBUG))
        print("TEMPLATE_DIRS: {}".format(settings.TMPL_DIRS))
        print("STATICFILES_DIRS: {}".format(settings.STATICFILES_DIRS))
        sep()
        print("MONGODB_NAME: {}".format(settings.MONGODB_NAME))
        print("MONGODB_URI: {}".format(settings.MONGODB_URI))
        sep()
        print("Connecting to mongodb ...")
        from biostar4.forum import models
        names = ", ".join(models.db.database_names())
        print("Databases: {}".format(names))

        print (models.User.objects.all())

        u_count = models.User.objects.all().count()
        print ("Found {} users in the database".format(u_count))
        sep()
        print("RECAPTCHA_ENABLED: {}".format(settings.RECAPTCHA_ENABLED))
        print("SECRET_KEY: {}".format(settings.SECRET_KEY))
        sep()
        print("EMAIL_BACKEND: {}".format(settings.EMAIL_BACKEND))

        #print("SECRET_KEY: {}".format(settings.SECRET_KEY))

        if options.get('test_email'):
            test_email()