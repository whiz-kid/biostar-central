from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    help = 'Runs a high performance server'

    def handle(self, *args, **options):
        from waitress import serve
        from whitenoise.django import DjangoWhiteNoise

        from biostar4 import wsgi
        app = DjangoWhiteNoise(wsgi.application)
        serve(app, host='0.0.0.0', port=8080)
