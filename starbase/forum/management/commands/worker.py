"""
Handles asynchronous tasks:

    - sending emails
    - awarding badges
    - cleaning up sessions
    - pruning notifications
    - generating sitemaps
    - updating the planet
    - sending daily or weekly digests
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Offline worker for Biostar."

    def add_arguments(self, parser):
        parser.add_argument('--foo', action="store_true", default=False)

    def handle(self, *args, **options):

        if options['foo']:
            print ("Foo")
