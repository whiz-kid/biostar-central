from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from biostar4.forum.models import *
from django.core.management import call_command


import os

class Command(BaseCommand):
    help = 'Resets the SQLITE database. Used during development'

    def add_arguments(self, parser):
        parser.add_argument('--reset',
            action='store_true',dest='reset', default=False,
            help='Completely resets the database')

    def handle(self, *args, **options):

        if options['reset']:
            fname = settings.DATABASES['default']['NAME']
            print ("*** resetting DATABASE=%s" % fname)
            if os.path.isfile(fname):
                print ("*** deleting %s" % fname)
                os.remove(fname)
            else:
                print("*** nothing to reset.")
            os.remove("biostar4/forum/migrations/0001_initial.py")
            call_command('makemigrations')

        # Migrate the database.
        call_command('migrate')
