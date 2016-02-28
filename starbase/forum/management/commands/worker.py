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
import os, logging
from django.core.management.base import BaseCommand, CommandError
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sites.models import Site
from django.template import loader
from django.conf import settings
from django.utils.encoding import smart_str

logger = logging.getLogger("command")

def path(*args):
    """Generates absolute paths"""
    return os.path.abspath(os.path.join(*args))


class Command(BaseCommand):
    help = "Offline worker for Biostar."

    def add_arguments(self, parser):
        parser.add_argument('--sitemap', action="store_true", default=False)

    def handle(self, *args, **options):

        if options['sitemap']:
            generate_sitemap()


def generate_sitemap():
    """
    Generates a sitemap and stores it the STATIC root as sitemap.xml.
    Set up your static web server to serve this file.
    Run it daily.
    """
    from biostar.apps.posts.models import Post

    sitemap = GenericSitemap({
        'queryset': Post.objects.filter(type__in=Post.TOP_LEVEL, status=Post.OPEN).exclude(type=Post.BLOG),
    })
    urlset = sitemap.get_urls()
    text = loader.render_to_string('sitemap.xml', {'urlset': urlset})
    text = smart_str(text)
    fname = path(settings.STATIC_ROOT, 'sitemap.xml')
    logger.info('saving sitemap to: {} '.format(fname))
    with open(fname, 'wt') as fp:
        fp.write(text)
        fp.close()
